# Cowork Skills

A collection of Claude Cowork skills. Each folder under `skills/` is a self-contained
skill with a `SKILL.md` (and any supporting scripts/assets). Drop them into your own
skills directory to use them.

## Skills

| Skill | Description |
|-------|-------------|
| [aios-capture](skills/aios-capture) | Capture useful information from the current chat into an "AIOS vault" at the end of a session or on request (`save this`, `/capture`). |
| [consolidate-memory](skills/consolidate-memory) | Reflective pass over your memory files — merge duplicates, fix stale facts, prune the index. |
| [explain-usage](skills/explain-usage) | Explain where a session's tokens went, with one simple chart in plain language. |
| [frontend-master](skills/frontend-master) | Generate and review frontend code — React/Next.js, React Native/Expo, Tailwind, and motion (Framer Motion, Reanimated, GSAP). |
| [llm-council](skills/llm-council) | Ask an "LLM Council" instead of a single model: members answer independently, rank each other anonymously, and a Chairman synthesizes the final answer. Based on karpathy/llm-council. |
| [morning](skills/morning) | Render a morning brief as a styled HTML artifact, or set it up as a recurring weekday task. |
| [schedule](skills/schedule) | Create or update a scheduled task that runs automatically ("every morning", "remind me in an hour", etc.). |
| [seedance-loop-prompt](skills/seedance-loop-prompt) | Generate a Seedance 2 prompt for a seamless looping background video. |
| [setup-cowork](skills/setup-cowork) | Guided Cowork setup — install role-matched plugins, connect tools, try a skill. |
| [skill-creator](skills/skill-creator) | Create, modify, and improve skills, and measure/benchmark skill performance. |
| [web-artifacts-builder](skills/web-artifacts-builder) | Build elaborate multi-component HTML artifacts with React, Tailwind CSS, and shadcn/ui. |

## Installing a skill

Copy the folder you want into your Cowork/Claude skills directory, for example:

```bash
cp -r skills/llm-council ~/.claude/skills/
```

Each skill's `SKILL.md` header describes when it triggers and how it works.

## License

Released under the [MIT License](LICENSE).
