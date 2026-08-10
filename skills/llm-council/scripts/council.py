#!/usr/bin/env python3
"""LLM Council — stdlib-only port of karpathy/llm-council.

3 stages:
  1. All council models answer the question in parallel.
  2. Each model ranks the anonymized answers of the others.
  3. A Chairman model synthesizes the final answer.

Usage:
  OPENROUTER_API_KEY=sk-or-... python council.py "question" --out report.md
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_COUNCIL = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]
DEFAULT_CHAIRMAN = "google/gemini-3-pro-preview"


def query_model(api_key, model, messages, timeout):
    """Single OpenRouter chat completion. Returns content string or None."""
    payload = json.dumps({"model": model, "messages": messages}).encode()
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
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        print(f"[warn] {model}: HTTP {e.code}: {body}", file=sys.stderr)
    except Exception as e:
        print(f"[warn] {model}: {type(e).__name__}: {e}", file=sys.stderr)
    return None


def query_parallel(api_key, models, messages, timeout):
    """Query all models in parallel. Returns {model: content_or_None}."""
    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        futures = {m: pool.submit(query_model, api_key, m, messages, timeout) for m in models}
        return {m: f.result() for m, f in futures.items()}


# ---------------------------------------------------------------- Stage 1

def stage1(api_key, models, query, timeout):
    messages = [{"role": "user", "content": query}]
    responses = query_parallel(api_key, models, messages, timeout)
    return [
        {"model": m, "response": r}
        for m, r in responses.items()
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


def stage2(api_key, models, query, stage1_results, timeout):
    labels = [chr(65 + i) for i in range(len(stage1_results))]
    label_to_model = {
        f"Response {label}": r["model"] for label, r in zip(labels, stage1_results)
    }
    responses_text = "\n\n".join(
        f"Response {label}:\n{r['response']}" for label, r in zip(labels, stage1_results)
    )
    prompt = RANKING_PROMPT.format(query=query, responses_text=responses_text)
    messages = [{"role": "user", "content": prompt}]
    responses = query_parallel(api_key, models, messages, timeout)
    stage2_results = [
        {"model": m, "ranking": r, "parsed_ranking": parse_ranking(r)}
        for m, r in responses.items()
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

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""


def stage3(api_key, chairman, query, stage1_results, stage2_results, timeout):
    stage1_text = "\n\n".join(
        f"Model: {r['model']}\nResponse: {r['response']}" for r in stage1_results
    )
    stage2_text = "\n\n".join(
        f"Model: {r['model']}\nRanking: {r['ranking']}" for r in stage2_results
    )
    prompt = CHAIRMAN_PROMPT.format(
        query=query, stage1_text=stage1_text, stage2_text=stage2_text
    )
    response = query_model(api_key, chairman, [{"role": "user", "content": prompt}], timeout)
    return {
        "model": chairman,
        "response": response or "Error: Unable to generate final synthesis.",
    }


# ---------------------------------------------------------------- Report

def build_report(query, stage1_results, stage2_results, label_to_model, agg, final):
    lines = ["# LLM Council Report", "", f"**Question:** {query}", ""]

    lines += ["## Final Answer (Chairman: {})".format(final["model"]), "", final["response"], ""]

    if agg:
        lines += ["## Aggregate Ranking (lower = better)", ""]
        lines += ["| # | Model | Avg rank | Votes |", "|---|-------|----------|-------|"]
        for i, a in enumerate(agg, 1):
            lines.append(f"| {i} | {a['model']} | {a['average_rank']} | {a['rankings_count']} |")
        lines.append("")

    lines += ["## Stage 1 — Individual Responses", ""]
    model_to_label = {v: k for k, v in label_to_model.items()}
    for r in stage1_results:
        label = model_to_label.get(r["model"], "")
        lines += [f"### {r['model']} ({label})", "", r["response"], ""]

    lines += ["## Stage 2 — Peer Reviews & Rankings", ""]
    lines += ["Anonymization map: " + ", ".join(f"{k} = {v}" for k, v in label_to_model.items()), ""]
    for r in stage2_results:
        lines += [f"### Reviewer: {r['model']}", "", r["ranking"], ""]

    return "\n".join(lines)


# ---------------------------------------------------------------- Main

def main():
    p = argparse.ArgumentParser(description="Run the LLM Council on a question.")
    p.add_argument("question", nargs="?", help="The question to ask the council")
    p.add_argument("--question-file", help="Read the question from a file")
    p.add_argument("--models", help="Comma-separated OpenRouter model IDs")
    p.add_argument("--chairman", default=DEFAULT_CHAIRMAN)
    p.add_argument("--out", help="Write markdown report to this path")
    p.add_argument("--json", dest="json_out", help="Write raw JSON results to this path")
    p.add_argument("--key-file", help="Read OPENROUTER_API_KEY from this file")
    p.add_argument("--timeout", type=float, default=120.0)
    args = p.parse_args()

    if args.question_file:
        with open(args.question_file, encoding="utf-8") as f:
            query = f.read().strip()
    elif args.question:
        query = args.question
    else:
        p.error("provide a question or --question-file")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key and args.key_file:
        with open(args.key_file, encoding="utf-8") as f:
            api_key = f.readline().strip()
    if not api_key:
        sys.exit("Error: set OPENROUTER_API_KEY env var or pass --key-file. Get a key at https://openrouter.ai/")

    models = args.models.split(",") if args.models else DEFAULT_COUNCIL
    models = [m.strip() for m in models if m.strip()]

    print(f"Council: {', '.join(models)} | Chairman: {args.chairman}", file=sys.stderr)

    print("Stage 1/3: collecting first opinions...", file=sys.stderr)
    stage1_results = stage1(api_key, models, query, args.timeout)
    if not stage1_results:
        sys.exit("Error: all council models failed to respond. Check your API key and credits.")
    print(f"  {len(stage1_results)}/{len(models)} models responded", file=sys.stderr)

    print("Stage 2/3: peer review and ranking...", file=sys.stderr)
    stage2_results, label_to_model = stage2(api_key, models, query, stage1_results, args.timeout)
    agg = aggregate_rankings(stage2_results, label_to_model)

    print("Stage 3/3: chairman synthesis...", file=sys.stderr)
    final = stage3(api_key, args.chairman, query, stage1_results, stage2_results, args.timeout)

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
