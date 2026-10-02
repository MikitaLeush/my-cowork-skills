---
name: "llm-council"
description: "Ask an \"LLM Council\" instead of a single model — based on karpathy/llm-council. Several council members (including a brutal Roaster who attacks the idea from every angle) answer the question independently and in parallel, then anonymously review and rank each other's answers, and a Chairman synthesizes the final response. Default mode runs entirely on Claude subagents (no API key needed); an optional OpenRouter mode runs real different models (free models by default, with automatic fallback when one is rate-limited) if the user has a key. Use whenever the user says \"ask the council\", \"LLM council\", \"council of models\", wants multiple independent takes on a question, wants an idea stress-tested or roasted, wants answers cross-checked and ranked, or wants the most robust possible answer to a hard or high-stakes question."
---

# LLM Council

Port of [karpathy/llm-council](https://github.com/karpathy/llm-council). Instead of one answer, run a 3-stage council:

1. **First opinions** — council members answer the question independently, in parallel.
2. **Review** — each member sees the others' answers anonymized as "Response A/B/C/D/E" (so it can't play favorites) and ranks them by accuracy and insight.
3. **Final response** — a Chairman reads all answers and rankings and writes one synthesized answer.

## Default mode: Claude subagent council (no API key)

You (Claude) orchestrate the council using parallel subagents via the Agent tool. Since all members share one underlying model, diversity comes from distinct reasoning stances — this is the point, so don't skip the personas.

### Stage 1 — First opinions

Spawn 5 subagents **in parallel (one block)**. Each gets the user's question plus one stance. Don't mention the council or other members — each must believe it's giving the definitive answer.

- **The Analyst**: "Answer with maximum rigor. Define terms, reason step by step, quantify where possible, state your confidence and assumptions explicitly."
- **The Skeptic**: "Answer, but lead with what's uncertain, commonly gotten wrong, or missing from the obvious answer. Challenge the question's premises if warranted."
- **The Lateral Thinker**: "Answer from first principles and unexpected angles. Prefer the insightful framing over the textbook one, but stay accurate."
- **The Practitioner**: "Answer as a hands-on expert would: concrete, actionable, grounded in how things actually work in practice, with real trade-offs."
- **The Roaster**: "Your job is to tear the idea apart. Assume it is flawed and hunt down every reason why. Examine it from every angle — technical, practical, economic, legal, social, motivational, second-order consequences, failure modes, hidden assumptions, and the things the person is conveniently not thinking about. Be brutally blunt and give zero flattery: do NOT soften anything to spare feelings or fit what the person wants to hear. Roast the idea and the reasoning behind it hard, with bite and wit, and mock the weak logic and lazy assumptions relentlessly. Name the single most damning problem plainly, then pile on every other flaw. Attack the idea and the thinking, not the person's worth as a human. Stay factually accurate the whole time — a roast only lands if it's true. End with the honest bottom line, however unflattering."

If the question needs current facts, tell every member to verify with web search so no one answers from stale memory. This matters most for The Roaster — a roast built on wrong facts is worthless, so it should confirm its ammunition is real.

### Stage 2 — Anonymous peer review

Shuffle the answers, label them Response A–E. Spawn 5 fresh reviewer subagents in parallel (fresh = they don't know who wrote what, including themselves). Each gets:

```
You are evaluating different responses to the following question:

Question: {question}

Here are the responses from different models (anonymized):

{Response A: ...\n\nResponse B: ...\n\n...Response E: ...}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section
```

Parse each FINAL RANKING and compute the average rank per response (lower = better). Rank on accuracy and insight — the Roaster's answer competes on the same terms; harshness alone is not merit, but a sharp, correct roast that surfaces real problems others missed should score well.

### Stage 3 — Chairman synthesis

Act as Chairman yourself (you have the most context). Synthesize all answers and rankings into one comprehensive, accurate final answer: weigh the peer rankings, note patterns of agreement/disagreement, and resolve conflicts on the merits rather than by majority vote. Fold the Roaster's strongest hits into the answer where they're valid — the point of including a roast is to make sure the final answer confronts the real problems head-on instead of flattering the user. If the user asked to be roasted, keep that blunt tone in the final answer too.

### Presenting results

- Give the Chairman's final answer in chat.
- Show the leaderboard briefly (e.g., "Council ranked the Skeptic's answer best, 1.25 avg").
- Offer (or write, if the user asked for a report) a full markdown report: final answer, leaderboard, all 5 answers with their stances, all 5 reviews. The side-by-side view is the main value of the council.
- Per AIOS rules: a saved report is generated content → `chats/YYYY-MM-DD-council-<topic>.md` (with the `chats/` frontmatter from `CLAUDE.md`), never `wiki/pages/` — the wiki only takes content through an ingest.

## Optional mode: real multi-model council via OpenRouter

If the user has an OpenRouter API key (`sk-or-v1-...`), `scripts/council.py` (stdlib-only) runs the original design with actually different models. **It uses free models by default** — no credits spent:

```bash
python scripts/council.py "question" --out report.md
```

- **Stances and the Roaster**: each seat gets one of the Stage 1 stances in its prompt (Analyst, Skeptic, Practitioner, Lateral Thinker, cycling) and **the last seat is always The Roaster**. A fallback model inherits the seat's stance, so the roast survives a rate-limited model. Answers are shuffled before review, and the report labels each answer and leaderboard row with its stance. `--no-roast` drops the Roaster seat; `--no-stances` sends the bare question (original karpathy behaviour). When you chair, apply the Stage 3 rule on the Roaster's hits as usual.
- **You are the Chairman.** The script runs stages 1–2 only (answers + anonymous peer rankings) and leaves the Final Answer section empty. Read its report, then do Stage 3 exactly as described above — you are the strongest model in the room and cost nothing extra. Present the result the same way (final answer in chat, leaderboard, report on request), and fill the report's Final Answer section if you save it. Only if the user asks for a non-Claude chairman, pass `--chairman <openrouter-model-id>`.
- **Free mode (default)**: council seats and a ranked fallback order come from `scripts/free_models.json`. When a model fails (rate-limited upstream, down, removed), the next unused model in that list takes its seat, so the council stays full. Edit that file to re-rank.
- **Account-wide cap**: free models share one limit per account — 20 requests/min and 50/day (1000/day once $10 of credits has ever been bought). A 4-seat run is 8 requests plus any fallbacks (the chairman is you, not a request), so ~6 runs/day on the free cap. When the daily cap hits, the script stops and says so — switching models can't help.
- **Free models churn**: run `python scripts/council.py --check-models` (no key needed) to list models that disappeared and new free ones not yet ranked. Update `free_models.json` from that.
- `--paid` uses the frontier preset (GPT, Gemini, Claude, Grok) and costs real credits. `--no-fallback` disables substitution.

Other flags: `--no-roast`, `--no-stances`, `--models a,b,c`, `--chairman model`, `--json out.json`, `--key-file path`, `--question-file path`, `--timeout secs`. Key lookup order: `OPENROUTER_API_KEY` env var → `--key-file` → `~/.llm-council-key` → ask the user. Never echo the key in full, and never write it into the vault or this skill folder (both sync/publish). Only use this mode when the user has a key — default to the subagent council otherwise. Report which models actually answered (the report header lists them; substitutions are logged to stderr).

## Notes

- A failed/timed-out council member is fine — proceed with whoever answered; note it to the user.
- Council runs cost ~11 subagent calls; for casual questions ask the user before firing the full council if it seems like overkill.
- The Roaster is a stance, not a license to be cruel to the person — it attacks the idea and the reasoning without flattery, but never demeans the human's worth.

