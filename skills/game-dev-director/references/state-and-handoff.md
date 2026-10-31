# Durable State and Handoff

## Project truth vs global continuity

Project-local durable docs are the technical source of truth.

The Brain vault (if used) is cross-project/global continuity and must stay compact.

Never copy large project docs into it.

## Conflicts

Recovery order and source-of-truth priority are in the global CLAUDE.md. Use
current local repo state to resolve conflicts: if global memory says M2 but the
repo-local handoff says M3 and git supports it, M3 wins.

## When to update

At every checkpoint listed in the global CLAUDE.md. Do not wait until the
session is almost dead if a checkpoint has already occurred.

## HANDOFF.md

Keep it concise and operational:
- last verified checkpoint;
- branch/commit if relevant;
- what was delivered;
- verification evidence;
- current blockers/risks;
- exact next milestone/task.

It is not a transcript. Keep only the last one or two sessions; move older
entries to `docs/ai/archive/`. It is read at every session start.

## CURRENT_TASK.md

Represent only the active task (finished-task logs go to `docs/ai/archive/`):
- goal;
- scope;
- acceptance criteria;
- status;
- blockers;
- next action.

## PROJECT_CONTEXT.md

Stable project identity, stack, architecture constraints, target platforms, and
workflow assumptions. Do not rewrite it every session, but update it when the
platform, stack, or project stage changes; a stale one misleads every recovery.

## Brain and native memory

If the Brain is installed, its format (`LAST_SESSION.md`, `THREADS.md`, `JOURNAL.md`) is owned by
`memory-keeper` and defined in `$BRAIN_HOME/850-Memory/MEMORY_PROTOCOL.md`.
Native Claude auto-memory never overrides project durable state.
