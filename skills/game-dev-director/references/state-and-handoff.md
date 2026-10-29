# Durable State and Handoff

## Project truth vs global continuity

Project-local durable docs are the technical source of truth.

The brain is cross-project/global continuity and must stay compact.

Never copy large project docs into the brain.

## Continuing-project recovery

Preferred `docs/ai/` order:

1. `HANDOFF.md`
2. `PROJECT_CONTEXT.md`
3. `CURRENT_TASK.md`
4. `git status --short`
5. relevant source files only

Use current local repo state to resolve conflicts. If global memory says M2 but
the repo-local handoff says M3 and git supports it, M3 wins.

## When to update

Update project durable state after:
- completed/accepted task;
- milestone checkpoint;
- important decision;
- blocker change;
- tests/manual acceptance;
- commit/merge/push that changes recovery point;
- before switching milestones.

Do not wait until the session is almost dead if a checkpoint has already occurred.

## HANDOFF.md

Keep it concise and operational:
- last verified checkpoint;
- branch/commit if relevant;
- what was delivered;
- verification evidence;
- current blockers/risks;
- exact next milestone/task.

It is not a transcript.

## CURRENT_TASK.md

Represent only the active task:
- goal;
- scope;
- acceptance criteria;
- status;
- blockers;
- next action.

## PROJECT_CONTEXT.md

Stable project identity, stack, architecture constraints, target platforms, and
workflow assumptions. Do not rewrite it every session.

## Brain global update

`LAST_SESSION.md` should be a bridge, not a duplicate:
- project name/path;
- current verified checkpoint;
- next action;
- pointer to repo-local durable state.

`THREADS.md` tracks ongoing cross-session threads/status.

`JOURNAL.md` records only meaningful developments.

## Native Claude auto-memory

Allowed for convenience facts such as:
- build/test commands;
- recurring debugging patterns;
- local tooling quirks.

It must not override project durable state.
