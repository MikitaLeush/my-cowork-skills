#!/usr/bin/env python3
"""LLM Council — stdlib-only port of karpathy/llm-council.

3 stages:
  1. All council models answer the question in parallel.
  2. Each model ranks the anonymized answers of the others.
  3. A Chairman synthesizes the final answer. By default that is the Claude
     session running the skill, so the script stops after stage 2.

Usage:
  OPENROUTER_API_KEY=sk-or-... python council.py "question" --out report.md
  python council.py --check-models     # which free models are gone / new

Free by default: council seats, chairman and the fallback order come from
free_models.json next to this file. When a model fails (upstream 429, downtime,
removed) the next unused model in that list takes the seat. When the ACCOUNT
hits its free daily cap, no other free model can answer either, so the run stops.
"""

import argparse
import json
import os
import random
import re
import sys
import threading
import time
import urllib.request
import urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
FREE_MODELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "free_models.json")

# --paid preset (costs credits)
PAID_COUNCIL = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]
PAID_CHAIRMAN = "claude"

# Chairman value meaning "skip stage 3": the Claude session running the skill is the
# strongest model available and already paid for, so it writes the final answer.
SESSION_CHAIRMAN = "claude"


def load_free_models():
    with open(FREE_MODELS_FILE, encoding="utf-8") as f:
        return json.load(f)


class Abort(Exception):
    """Nothing else can succeed this run: bad key, or the account's daily free cap."""


class Pool:
    """Ranked fallback list shared by the seats of one stage. A model that failed
    is skipped for the rest of the run, and no two seats hold the same model."""

    def __init__(self, fallbacks):
        self.order = list(fallbacks)
        self.dead = set()
        self.claimed = set()
        self.lock = threading.Lock()
        self.aborted = None

    def seat(self, models):
        with self.lock:
            self.claimed = set(models)

    def replace(self, failed):
        with self.lock:
            self.dead.add(failed)
            for m in self.order:
                if m not in self.dead and m not in self.claimed:
                    self.claimed.add(m)
                    return m
            return None


def classify(code, body):
    """'abort' | 'wait' | 'next' for an HTTP error from OpenRouter."""
    low = body.lower()
    if code == 401:
        return "abort"
    if code == 429 and ("per-day" in low or "per day" in low):
        return "abort"
    if code == 429 and ("per-min" in low or "per minute" in low):
        return "wait"
    return "next"  # upstream 429, 404 removed, 402, 5xx


def query_model(api_key, model, messages, timeout):
    """Single OpenRouter chat completion. Returns content, or None when this model
    failed and another should be tried. Raises Abort when no model can succeed."""
    payload = json.dumps({"model": model, "messages": messages}).encode()
    for attempt in range(2):
        req = urllib.request.Request(
            OPENROUTER_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            if "error" in data:  # upstream failures can arrive inside a 200
                print(f"[warn] {model}: {str(data['error'])[:300]}", file=sys.stderr)
                return None
            content = data["choices"][0]["message"].get("content")
            if not content or not content.strip():
                print(f"[warn] {model}: empty answer", file=sys.stderr)
                return None
            return content
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            print(f"[warn] {model}: HTTP {e.code}: {body}", file=sys.stderr)
            kind = classify(e.code, body)
            if kind == "abort":
                raise Abort(f"HTTP {e.code}: {body}")
            if kind == "wait" and attempt == 0:
                delay = min(float(e.headers.get("Retry-After") or 20), 60)
                print(f"[info] per-minute limit, retrying {model} in {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
                continue
            return None
        except Exception as e:
            print(f"[warn] {model}: {type(e).__name__}: {e}", file=sys.stderr)
            return None
    return None


def query_seat(api_key, pool, model, messages, timeout):
    """Ask one seat, walking down the fallback list until a model answers.
    Returns (model_that_answered, content) or (None, None)."""
    if model in pool.dead:  # failed in an earlier stage: don't spend a request on it
        model = pool.replace(model)
    while model and not pool.aborted:
        try:
            content = query_model(api_key, model, messages, timeout)
        except Abort as e:
            pool.aborted = str(e)
            return None, None
        if content is not None:
            return model, content
        nxt = pool.replace(model)
        if nxt:
            print(f"[info] {model} failed -> {nxt} takes the seat", file=sys.stderr)
        model = nxt
    return None, None


def query_parallel(api_key, pool, models, seat_messages, timeout):
    """Query all seats in parallel, seat i with seat_messages[i]. A fallback model
    inherits the seat's messages, so a seat keeps its stance whoever fills it.
    Returns [(answered_by, content)] per seat."""
    pool.seat(models)
    with ThreadPoolExecutor(max_workers=len(models)) as ex:
        futures = [ex.submit(query_seat, api_key, pool, m, msgs, timeout)
                   for m, msgs in zip(models, seat_messages)]
        return [f.result() for f in futures]


# ---------------------------------------------------------------- Stage 1

# Same stances as the subagent council in SKILL.md. Different models already give
# diversity; the stances make sure someone is actually assigned to attack the idea.
STANCES = [
    ("The Analyst", "Answer with maximum rigor. Define terms, reason step by step, quantify where possible, state your confidence and assumptions explicitly."),
    ("The Skeptic", "Answer, but lead with what's uncertain, commonly gotten wrong, or missing from the obvious answer. Challenge the question's premises if warranted."),
    ("The Practitioner", "Answer as a hands-on expert would: concrete, actionable, grounded in how things actually work in practice, with real trade-offs."),
    ("The Lateral Thinker", "Answer from first principles and unexpected angles. Prefer the insightful framing over the textbook one, but stay accurate."),
]
ROASTER = ("The Roaster", "Your job is to tear the idea apart. Assume it is flawed and hunt down every reason why. Examine it from every angle — technical, practical, economic, legal, social, motivational, second-order consequences, failure modes, hidden assumptions, and the things the person is conveniently not thinking about. Be brutally blunt and give zero flattery: do NOT soften anything to spare feelings or fit what the person wants to hear. Roast the idea and the reasoning behind it hard, with bite and wit, and mock the weak logic and lazy assumptions relentlessly. Name the single most damning problem plainly, then pile on every other flaw. Attack the idea and the thinking, not the person's worth as a human. Stay factually accurate the whole time — a roast only lands if it's true. End with the honest bottom line, however unflattering.")


def assign_stances(n, roast=True):
    """One stance per seat. The last seat is always the Roaster (with 2+ seats);
    the rest cycle through STANCES."""
    if not roast or n < 2:
        return [STANCES[i % len(STANCES)] for i in range(n)]
    return [STANCES[i % len(STANCES)] for i in range(n - 1)] + [ROASTER]


def stage1(api_key, pool, models, query, timeout, stances=None):
    if stances is None:  # plain run: every seat gets the bare question
        seat_messages = [[{"role": "user", "content": query}] for _ in models]
        stances = [("", "")] * len(models)
    else:
        # Stance goes in the user turn, not a system message: several free models
        # (e.g. Gemma) reject or ignore the system role.
        seat_messages = [
            [{"role": "user", "content": f"{instr}\n\nQuestion:\n{query}"}]
            for _, instr in stances
        ]
    responses = query_parallel(api_key, pool, models, seat_messages, timeout)
    return [
        {"model": m, "stance": name, "response": r}
        for (m, r), (name, _) in zip(responses, stances)
        if r is not None
    ]


# ---------------------------------------------------------------- Stage 2

RANKING_PROMPT = """You are evaluating different responses to the following question:

Question: {query}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""


def stage2(api_key, pool, models, query, stage1_results, timeout):
    # Shuffle so a stance never sits at a predictable label (the Roaster is always the
    # last seat, and would otherwise always be the last response).
    shuffled = random.sample(stage1_results, len(stage1_results))
    labels = [chr(65 + i) for i in range(len(shuffled))]
    label_to_model = {
        f"Response {label}": r["model"] for label, r in zip(labels, shuffled)
    }
    responses_text = "\n\n".join(
        f"Response {label}:\n{r['response']}" for label, r in zip(labels, shuffled)
    )
    prompt = RANKING_PROMPT.format(query=query, responses_text=responses_text)
    messages = [{"role": "user", "content": prompt}]
    responses = query_parallel(api_key, pool, models, [messages] * len(models), timeout)
    stage2_results = [
        {"model": m, "ranking": r, "parsed_ranking": parse_ranking(r)}
        for m, r in responses
        if r is not None
    ]
    return stage2_results, label_to_model


def parse_ranking(text):
    if "FINAL RANKING:" in text:
        section = text.split("FINAL RANKING:", 1)[1]
        numbered = re.findall(r"\d+\.\s*Response [A-Z]", section)
        if numbered:
            return [re.search(r"Response [A-Z]", m).group() for m in numbered]
        return re.findall(r"Response [A-Z]", section)
    return re.findall(r"Response [A-Z]", text)


def aggregate_rankings(stage2_results, label_to_model):
    positions = defaultdict(list)
    for r in stage2_results:
        for pos, label in enumerate(r["parsed_ranking"], start=1):
            if label in label_to_model:
                positions[label_to_model[label]].append(pos)
    agg = [
        {
            "model": m,
            "average_rank": round(sum(p) / len(p), 2),
            "rankings_count": len(p),
        }
        for m, p in positions.items()
        if p
    ]
    agg.sort(key=lambda x: x["average_rank"])
    return agg


# ---------------------------------------------------------------- Stage 3

CHAIRMAN_PROMPT = """You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, and then ranked each other's responses.

Original Question: {query}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement
- If a member answered as "The Roaster" (assigned to tear the idea apart), fold its valid hits into your answer so it confronts the real problems head-on; discount harshness that isn't backed by facts

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""


def stage3(api_key, pool, chairman, query, stage1_results, stage2_results, timeout):
    stage1_text = "\n\n".join(
        f"Model: {r['model']}{stance_suffix(r)}\nResponse: {r['response']}" for r in stage1_results
    )
    stage2_text = "\n\n".join(
        f"Model: {r['model']}\nRanking: {r['ranking']}" for r in stage2_results
    )
    prompt = CHAIRMAN_PROMPT.format(
        query=query, stage1_text=stage1_text, stage2_text=stage2_text
    )
    pool.seat([chairman])
    used, response = query_seat(api_key, pool, chairman, [{"role": "user", "content": prompt}], timeout)
    return {
        "model": used or chairman,
        "response": response or "Error: Unable to generate final synthesis.",
    }


# ---------------------------------------------------------------- Report

def stance_suffix(r):
    return f" — {r['stance']}" if r.get("stance") else ""


def build_report(query, stage1_results, stage2_results, label_to_model, agg, final):
    stance_of = {r["model"]: r.get("stance", "") for r in stage1_results}
    lines = ["# LLM Council Report", "", f"**Question:** {query}", ""]

    if final:
        lines += ["## Final Answer (Chairman: {})".format(final["model"]), "", final["response"], ""]
    else:
        lines += ["## Final Answer (Chairman: Claude)", "",
                  "_Not written by this script: the Claude session that ran it synthesizes the "
                  "final answer from the stages below._", ""]

    if agg:
        lines += ["## Aggregate Ranking (lower = better)", ""]
        lines += ["| # | Model | Stance | Avg rank | Votes |", "|---|-------|--------|----------|-------|"]
        for i, a in enumerate(agg, 1):
            lines.append(f"| {i} | {a['model']} | {stance_of.get(a['model']) or '-'} "
                         f"| {a['average_rank']} | {a['rankings_count']} |")
        lines.append("")

    lines += ["## Stage 1 — Individual Responses", ""]
    model_to_label = {v: k for k, v in label_to_model.items()}
    for r in stage1_results:
        label = model_to_label.get(r["model"], "")
        lines += [f"### {r['model']}{stance_suffix(r)} ({label})", "", r["response"], ""]

    lines += ["## Stage 2 — Peer Reviews & Rankings", ""]
    lines += ["Anonymization map: " + ", ".join(f"{k} = {v}" for k, v in label_to_model.items()), ""]
    for r in stage2_results:
        lines += [f"### Reviewer: {r['model']}", "", r["ranking"], ""]

    return "\n".join(lines)


# ---------------------------------------------------------------- Main

def check_models():
    """Compare free_models.json against OpenRouter's live catalogue (no key needed)."""
    with urllib.request.urlopen(OPENROUTER_MODELS_URL, timeout=30) as resp:
        live = {m["id"]: m for m in json.loads(resp.read().decode("utf-8"))["data"]}
    cfg = load_free_models()
    listed = set(cfg["fallbacks"]) | set(cfg["council"]) | ({cfg["chairman"]} - {SESSION_CHAIRMAN})
    known = listed | {k.strip() for key in cfg.get("_excluded", {}) for k in key.split(",")}
    gone = sorted(m for m in listed if m not in live)
    new = sorted(m for m in live if m.endswith(":free") and m not in known)
    print(f"free_models.json updated {cfg.get('updated', '?')}")
    print("gone from OpenRouter (remove these):" if gone else "every listed model is still live")
    for m in gone:
        print("  - " + m)
    if new:
        print("new free models, not ranked yet:")
        for m in new:
            print(f"  + {m}  (ctx {live[m].get('context_length')})")


def main():
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Run the LLM Council on a question.")
    p.add_argument("question", nargs="?", help="The question to ask the council")
    p.add_argument("--question-file", help="Read the question from a file")
    p.add_argument("--models", help="Comma-separated OpenRouter model IDs")
    p.add_argument("--chairman", help="Chairman: 'claude' (default, the session synthesizes) or an OpenRouter model ID")
    p.add_argument("--paid", action="store_true", help="Use the paid frontier preset instead of free models")
    p.add_argument("--no-fallback", action="store_true", help="Do not replace failed models")
    p.add_argument("--no-roast", action="store_true", help="Keep the stances but drop the Roaster seat")
    p.add_argument("--no-stances", action="store_true", help="Send every seat the bare question (original karpathy behaviour)")
    p.add_argument("--check-models", action="store_true", help="Report gone/new free models and exit")
    p.add_argument("--out", help="Write markdown report to this path")
    p.add_argument("--json", dest="json_out", help="Write raw JSON results to this path")
    p.add_argument("--key-file", help="Read OPENROUTER_API_KEY from this file")
    p.add_argument("--timeout", type=float, default=120.0)
    args = p.parse_args()

    if args.check_models:
        return check_models()

    if args.question_file:
        with open(args.question_file, encoding="utf-8") as f:
            query = f.read().strip()
    elif args.question:
        query = args.question
    else:
        p.error("provide a question or --question-file")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    key_file = args.key_file or os.path.join(os.path.expanduser("~"), ".llm-council-key")
    if not api_key and os.path.exists(key_file):
        with open(key_file, encoding="utf-8") as f:
            api_key = f.readline().strip()
    if not api_key:
        sys.exit("Error: set OPENROUTER_API_KEY, put the key in ~/.llm-council-key, or pass --key-file. Get a key at https://openrouter.ai/")

    if args.paid:
        council, chairman, fallbacks = PAID_COUNCIL, PAID_CHAIRMAN, []
    else:
        cfg = load_free_models()
        council, chairman, fallbacks = cfg["council"], cfg["chairman"], cfg["fallbacks"]
    models = [m.strip() for m in args.models.split(",") if m.strip()] if args.models else council
    chairman = args.chairman or chairman
    pool = Pool([] if args.no_fallback else fallbacks)

    stances = None if args.no_stances else assign_stances(len(models), roast=not args.no_roast)

    print(f"Council: {', '.join(models)} | Chairman: {chairman}", file=sys.stderr)
    if stances:
        print("Stances: " + ", ".join(f"{m} = {s}" for m, (s, _) in zip(models, stances)), file=sys.stderr)

    def stop_if_aborted():
        if pool.aborted:
            sys.exit("Error: stopping, no other model can help: " + pool.aborted[:300] +
                     "\n(Free models share one account-wide cap: 50 requests/day, or 1000/day once"
                     " $10 of credits has been bought. It resets daily.)")

    print("Stage 1/3: collecting first opinions...", file=sys.stderr)
    stage1_results = stage1(api_key, pool, models, query, args.timeout, stances)
    stop_if_aborted()
    if not stage1_results:
        sys.exit("Error: every council model and fallback failed to respond.")
    print(f"  {len(stage1_results)}/{len(models)} seats answered: "
          + ", ".join(r["model"] for r in stage1_results), file=sys.stderr)

    print("Stage 2/3: peer review and ranking...", file=sys.stderr)
    reviewers = [r["model"] for r in stage1_results]  # known-alive models
    stage2_results, label_to_model = stage2(api_key, pool, reviewers, query, stage1_results, args.timeout)
    stop_if_aborted()
    agg = aggregate_rankings(stage2_results, label_to_model)

    if chairman == SESSION_CHAIRMAN:
        print("Stage 3/3: left to Claude (chairman) - synthesize from the report.", file=sys.stderr)
        final = None
    else:
        print("Stage 3/3: chairman synthesis...", file=sys.stderr)
        final = stage3(api_key, pool, chairman, query, stage1_results, stage2_results, args.timeout)

    report = build_report(query, stage1_results, stage2_results, label_to_model, agg, final)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {args.out}", file=sys.stderr)
    else:
        print(report)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "question": query,
                    "stage1": stage1_results,
                    "stage2": stage2_results,
                    "stage3": final,
                    "metadata": {"label_to_model": label_to_model, "aggregate_rankings": agg},
                },
                f,
                indent=2,
            )
        print(f"JSON written to {args.json_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
