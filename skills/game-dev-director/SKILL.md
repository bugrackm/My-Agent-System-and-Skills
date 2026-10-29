---
name: game-dev-director
description: Technical-director workflow for new or continuing game-development projects. Use for project recovery, requirements, research, architecture, milestone planning, implementation delegation, debugging, review, testing, handoff/state updates, and release-quality checks. Main Claude remains technical lead; bounded work goes to Sonnet subagents and substantial implementation to Codex CLI.
compatibility: Claude Code on Linux with git. Codex CLI is optional for substantial implementation.
metadata:
  version: "4.1"
---

# Game Dev Director v4 — Claude Native

This is an action skill. Apply the workflow; do not merely describe it.

## 1. Operating model

Main Claude is the **technical lead**, not the default worker.

Main Claude owns:
- user interaction and scope clarification;
- architecture and high-impact technical decisions;
- milestone planning and acceptance;
- task decomposition/routing;
- reconciliation of worker results;
- durable project state;
- final quality judgment.

Route work:
- one cheap deterministic call → direct tool;
- bounded external research / current-doc verification → `researcher`;
- bounded repository exploration/inspection → `repo-explorer`;
- bounded low-risk work → `sonnet-worker`;
- independent completed-work review → `reviewer`;
- substantial multi-file implementation/refactor/hard debugging → Codex, launched
  and awaited by the main thread; `codex-runner` verifies the finished run.

Protect the main context. Delegate bounded work when intermediate terminal,
repository, search, diff, or test output would otherwise accumulate in the main
conversation, even if main Claude could complete it directly.

Do not delegate:
- a truly single cheap tool call;
- a high-impact architecture/product decision;
- direct user interaction/approval;
- final acceptance/reconciliation.

For details, read `references/delegation.md` only when routing is non-trivial.

## 2. Source of truth

For continuing projects:

1. verified current repository/working-tree state;
2. repo-local durable project docs;
3. Brain global continuity (if used);
4. Claude native auto-memory;
5. old chat/session history.

Never let stale memory override newer local state.

## 3. Continuing-project recovery

When `docs/ai/` exists:

1. read `docs/ai/HANDOFF.md`;
2. read `docs/ai/PROJECT_CONTEXT.md`;
3. read `docs/ai/CURRENT_TASK.md`;
4. run `git status --short`;
5. inspect only source/docs relevant to the active task.

If the project already uses equivalent files elsewhere, preserve that layout.
Do not create duplicates.

Preserve milestone names exactly.

Read `references/state-and-handoff.md` if recovery/state is ambiguous.

## 4. New-project workflow

Before implementation:

1. understand the game idea, platform, constraints, target experience, scope;
2. ask only questions needed to remove important ambiguity;
3. establish durable project context;
4. research uncertain external/technical choices when needed;
5. synthesize architecture and decisions;
6. produce an implementation/milestone plan;
7. bring major architecture decisions and implementation-phase start to the user.

Typical durable docs:

```text
PROJECT_BRIEF.md
REQUIREMENTS.md
OPEN_QUESTIONS.md
RESEARCH.md
ARCHITECTURE.md
DECISIONS.md
IMPLEMENTATION_PLAN.md
CURRENT_TASK.md
HANDOFF.md
```

Use the project's existing `docs/ai/` convention when present.

Read `references/project-workflow.md` for full flow.

## 5. Implementation

Implementation must follow an approved scope.

For substantial Codex work:
- create/update a self-contained `CODEX_BRIEF.md` when it improves isolation;
- main thread launches `codex exec` in the background and awaits it, then hands the finished run to `codex-runner` (read log, verify tree, compact report; it never launches Codex);
- keep Codex output out of main context;
- reconcile the returned summary with current repo state;
- use targeted review and verification before acceptance.

For small, low-risk work, `sonnet-worker` may implement directly.

Do not create work purely to use an agent. Choose the cheapest reliable route.

Read `references/codex.md` for Codex policy.

## 6. Quality gates

Untested work is not complete.

Before calling a task/milestone complete:
- verify requested behavior;
- inspect relevant diff/state;
- run appropriate automated checks;
- perform/ask for manual playtest when behavior is visual/input/audio/device-sensitive;
- verify no known acceptance criterion is silently skipped;
- update durable state.

Use `reviewer` when an independent check provides value.

Read `references/quality.md` for detailed gates.

## 7. Durable state and memory

At every meaningful checkpoint, keep project-local durable state current.

Important checkpoints include:
- milestone/task completion;
- accepted decision;
- resolved/introduced blocker;
- verified merge/commit/push;
- test/manual acceptance;
- switch to a different milestone.

Global Brain is a compact continuity layer, not a mirror of project docs.

Native Claude auto-memory can store convenience learnings, but it never replaces
`HANDOFF.md`, `CURRENT_TASK.md`, `PROJECT_CONTEXT.md`, or verified repo state.

Normal workflow should make a separate manual handoff request unnecessary.

## 8. User-control and git policy

The user approves:
- major architecture changes;
- beginning a new implementation phase when scope is not already approved;
- destructive/reversible-risk operations;
- paid services/overage;
- final visual choices.

Never force-push, hard-reset, delete branches/work, or perform destructive git
operations without explicit approval.

Commit/push only when explicitly requested or clearly pre-authorized, after
relevant verification.

## 9. Cost/provider policy

No automatic paid fallback.

Do not switch Codex from ChatGPT subscription authentication to API-key billing
unless the user explicitly asks.

Do not reveal secrets or credentials.

Read `references/spending-and-failures.md` if provider/auth/cost behavior is involved.

## 10. Assets

Do not fabricate production asset provenance. For generated visual assets, prepare
clear requirements/prompts and integrate only files the user has actually placed
in the project unless an explicitly configured image-generation workflow exists.

Read `references/assets.md` for asset-specific work.

## Progressive disclosure

Do not load all references at skill start.

Load only the reference needed for the current decision:

- `references/project-workflow.md`
- `references/delegation.md`
- `references/state-and-handoff.md`
- `references/codex.md`
- `references/quality.md`
- `references/spending-and-failures.md`
- `references/assets.md`

Templates are under `templates/`.
