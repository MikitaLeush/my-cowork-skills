# Cowork Skills

A collection of Claude Cowork skills. Each folder under `skills/` is a self-contained
skill with a `SKILL.md` (and any supporting scripts/assets). Drop them into your own
skills directory to use them.

## Skills

| Skill | Description |
|-------|-------------|
| [aios-capture](skills/aios-capture) | Capture useful information from the current chat into an "AIOS vault" at the end of a session or on request (`save this`, `/capture`). |
| [frontend-master](skills/frontend-master) | Generate and review frontend code — React/Next.js, React Native/Expo, Tailwind, and motion (Framer Motion, Reanimated, GSAP). |
| [llm-council](skills/llm-council) | Ask an "LLM Council" instead of a single model: members answer independently, rank each other anonymously, and a Chairman synthesizes the final answer. Based on karpathy/llm-council. |
| [scrollcraft](skills/scrollcraft) | Build a premium scroll-driven landing page for any business — scrubbed video, pinned sections, sideways rails, pointer-reactive scenes. Ships its own engine, asset generator (kie.ai, needs `KIE_AI_API_KEY`) and verification scripts. |
| [seedance-loop-prompt](skills/seedance-loop-prompt) | Generate a Seedance 2 prompt for a seamless looping background video. |

## Installing a skill

Copy the folder you want into your Cowork/Claude skills directory, for example:

```bash
cp -r skills/llm-council ~/.claude/skills/
```

Each skill's `SKILL.md` header describes when it triggers and how it works.

## License

Released under the [MIT License](LICENSE).
