---
name: aios-capture
description: Capture useful information from the current chat into the AIOS vault. Use at the end of EVERY Cowork session, and whenever the user says "save this", "capture", "log to aios", "/capture", or when a chat produced insights, decisions, new information, research findings, or project work worth keeping. Auto-detects which machine it is running on.
---

# aios-capture — chat → AIOS vault

Goal: every useful chat leaves a trace in AIOS.

## Step 0 — find the vault (machine detection)

The vault's absolute path differs per machine, so never hardcode it.

1. **Prefer what is already there.** If a folder is already connected and
   its root holds a `CLAUDE.md` carrying the AIOS schema, that is the
   vault. Use it and skip the rest of this step.
2. Otherwise try these known paths in order with
   `request_cowork_directory` — they are hints, not a contract:
   `D:\Apps\vallets\aios`, then `C:\Users\nikit\work\aios`.
3. If neither exists, ask the user where the vault is on this machine and
   offer to add that path to the list above.

## Step 1 — detect the vault layout

Two layouts exist; check the vault root:

- **Organizer layout** — the root contains a `vault/` folder with
  `vault/00-inbox/`: captures go to `vault/00-inbox/cowork/` and session
  summaries to `vault/_sessions/` (steps A below).
- **Portable-vault layout** — the root contains `CLAUDE.md` and `chats/`:
  read that `CLAUDE.md` and follow its session protocol — one file in
  `chats/<date>-<slug>.md` (step B below). No organizer runs on this
  layout.

## Step 2 — triage

If the chat produced nothing durable (small talk, trivial lookup), say so
and stop — do not write empty files. Date as `YYYY-MM-DD`; short
kebab-case slug for the chat topic.

## Step 3A — organizer layout

1. **Capture file** → `vault/00-inbox/cowork/<date>-<slug>.md`, ALWAYS in
   English, with frontmatter:

   ```yaml
   ---
   type: chat-capture
   date: <YYYY-MM-DD>
   source: cowork
   status: raw
   ---
   ```

   Sections (omit any that are empty):
   - `## Insights` — distilled takeaways and conclusions
   - `## New information` — facts learned, each bullet self-contained (a
     small local model processes this file — no references like "see above")
   - `## Decisions` — what was decided and why
   - `## Project updates` — project name + what changed + next steps
   - `## References` — links and sources found during the chat

2. **Session summary** → `vault/_sessions/<date>-<slug>.md`, frontmatter
   `type: session`, `date`, `tags: [session, cowork]`. Short: what was
   asked, what was done, open follow-ups.

3. **Project work.** Code and project files live in
   `<root>\projects\<project-slug>\` — NOT inside `vault/`. For any
   project touched, create/update `vault/projects/<project-slug>.md`
   (frontmatter `origin: chat`, status, key decisions, next steps).

4. Do NOT call Ollama and do NOT re-index — the scheduled organizer
   (`organizer/organize.py`) does both.

## Step 3B — portable-vault layout

Write one file `chats/<date>-<slug>.md` exactly per the vault's
`CLAUDE.md`:

```markdown
---
date: <YYYY-MM-DD>
title: Short title
machine: (machineName from system/machine.json, or "unknown")
tags: [topic1, topic2]
---
## Summary
2-6 sentences: what was done, decided, produced.
## Artifacts
- links to files created/changed (relative paths)
## Follow-ups
- [ ] anything left open (also add to tasks/tasks.md if important)
```

If the session changed the system itself, also append an entry to
`system/build-log.md`. Add important follow-ups to `tasks/tasks.md`
(format: `- [ ] text !p1 @YYYY-MM-DD #tag`).

## Step 4 — report

Report the paths written, and which machine/layout was detected.

## Rules

- English always, even for Russian chats.
- Organizer layout: never write generated content directly into
  `vault/knowledge/`, `vault/clients/`, or `vault/transcripts/` — only
  the organizer may, and only with `origin: chat` frontmatter.
- One capture file per session; if it already exists, append to it.
- Facts over prose: short, atomic, self-contained bullets.
