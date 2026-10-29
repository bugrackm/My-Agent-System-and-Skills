---
title: Memory Protocol
created: YYYY-MM-DD
modified: YYYY-MM-DD
type: reference
status: active
tags: [memory, protocol]
---

# Memory Protocol

This is the detailed reference for writing discipline. It is not read every
session — only when writing memory or when a boundary case needs clarifying.
`VAULT.md` is enough for day-to-day use.

## Purpose

**Reliable continuity across sessions at low token cost.**

This system does not use: embeddings, a vector database, an external memory
API, an always-running daemon, or automatic transcript archiving. The semantic
author of memory is the agent; the hook, if present, only provides lifecycle
events and small context injection.

## File roles

### `CORE.md`
Only high-signal, long-lived working preferences. Project history does not
accumulate here. It changes rarely; update it when a rule genuinely changes.

### `LAST_SESSION.md`
Short summary of the last meaningful checkpoint. Not a transcript. **Overwritten**
— not accumulated. Goal: the minimum the next session needs to know where to
continue. Project/path, current checkpoint, next concrete step.

### `THREADS.md`
Only active / paused / waiting work. Not updated on every small step. Closed
threads are removed from here. Status vocabulary: 🟢 active · 🟡 in progress ·
🔴 blocked · ⚪ paused

### `JOURNAL.md`
Long-lived milestones and "why did we do it this way?" records. Not every
session goes here. Condition for adding: if someone asks in six months "why was
this decision made?", the answer should be here. Append-only, with a date
heading.

### `300-Projects/PROJECT_INDEX.md`
Helps find projects without moving them into the vault: absolute path, type,
status. A path is not a permanent identity; update it if the project moves.

## Meaningful checkpoint

Updating memory is part of the work when any of these happens:

- a milestone/phase is completed
- an important decision is made
- a blocker or risk changes
- the next concrete step changes
- the session is about to close
- a long-session checkpoint reminder arrives

## The writer: `memory-keeper`

Memory is written not by the main thread but by the cheap `memory-keeper`
agent (Sonnet, in the background). The main thread decides what happened; the
agent decides where and how to write it. The brief stays short: project/path,
what was done, decisions and why, current checkpoint, next concrete step, what
was learned, threads whose status changed.

Triggers:

- a meaningful checkpoint (list above)
- the hook's Stop reminder: at least 4 prompts since the last write; if nothing
  durable happened, nothing is written and the turn closes
- a `[Brain compaction checkpoint]` block after context compaction
- `[Brain recovery required]` at session start: the previous session ended
  without a memory write; the transcript path is given to the agent in recovery
  mode, and it extracts a digest (e.g. with `runtime/tools/transcript-digest.py`,
  if installed)

Routine maintenance is not reported to the user; only an `ATTENTION` line is
relayed.

Update order:

1. Verify current local state.
2. If needed, update the project's durable state first.
3. Write the short `LAST_SESSION.md` summary.
4. `THREADS.md` only if something changed.
5. `PROJECT_INDEX.md` only if a project is new/moved/changed status.
6. `JOURNAL.md` only if there is a long-lived decision or milestone.
7. `500-Knowledge/` only if there is a reusable technical lesson.
8. Health check (e.g. `runtime/tools/vault-doctor.py`, if installed) → commit → push.

## Writing conventions

- **`Learned:`** — a `LAST_SESSION` card ends with this one-line field if
  something was learned in the session. A reusable lesson also becomes a
  `500-Knowledge/` note (linked with `[[wikilink]]`).
- **Close with evidence** — when closing an item in `THREADS.md`, write an
  evidence line: a commit, a test, a manual test, or the user's acceptance. Work
  without evidence is not closed.
- **Supersession** — a reversed decision in the JOURNAL is not deleted; add
  `> Invalid: YYYY-MM-DD — [[new decision]]` beneath it, and record the new
  decision as a separate entry.
- **Lossless archive** — when the JOURNAL exceeds 250 lines, the oldest entries
  move verbatim to `900-Archive/journal-YYYY.md`; they are not summarized.

## Maintenance: `vault-doctor`

An optional read-only health check: missing frontmatter, broken wikilinks,
stale threads, size limits, commit/push status, secret patterns, runtime drift
(hooks in `settings.json`, `~/.claude` symlinks). `memory-keeper` runs it after
every write; if there is an ERROR, the user is told.

## Project documents

If a project keeps its own durable documents (`docs/ai/` or equivalent), they
are the source of project truth. The recovery order is not changed:

1. `HANDOFF.md` (if present)
2. `PROJECT_CONTEXT.md`
3. `CURRENT_TASK.md`
4. `git status --short`
5. only the source files needed to verify the next task

Milestone identity is preserved exactly; it is not renamed or renumbered. A
completed milestone is not reopened unless repo evidence says otherwise. The
contents of these files are not copied into the vault.

Size targets: `PROJECT_CONTEXT.md` ≈1500 words, `CURRENT_TASK.md` ≈700,
`HANDOFF.md` ≈900.

## Session rotation

- Same active task + high context: compact, continue.
- Milestone boundary / task change / end of session / very large context: write
  a durable handoff, open a fresh session. Do not start the next milestone in
  the same session.

## Never written

- conversation transcripts, raw agent logs, full diff/log dumps
- every tool call, transient debug noise
- secrets / API keys / tokens / cookies / passwords / SSH keys
- unrelated project detail
- unverified speculation presented as fact

## Hook contract (optional layer)

A hook can be installed to give the vault automatic continuity. Its contract:

- at session start it injects a **bounded** package (`LAST_SESSION`, active
  `THREADS`, a `docs/ai/HANDOFF.md` excerpt plus the recovery order) — not the whole vault
- it reminds about a checkpoint at prompts 12 and 24 of a long session
- at Stop, if a long span is unwritten, it reminds once to run `memory-keeper`;
  after compaction it asks for a checkpoint
- if a meaningful session closed without a memory write, it leaves a marker
  with the transcript path; the next session starts recovery
- if `settings.json` has lost one of the hooks in the template, it reports the
  drift
- on error it **fails open** and never breaks the session
- it does not produce semantic summaries or write memory in place of the agent

The hook is not required. The vault can be used fully by any agent that follows
the `VAULT.md` reading order.
