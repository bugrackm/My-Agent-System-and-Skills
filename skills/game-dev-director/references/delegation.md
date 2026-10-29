# Delegation and Main-Context Preservation

## Goal

Preserve the main Opus context for technical leadership, architecture, synthesis,
acceptance, and user decisions.

A task being "easy enough for the parent" is not by itself a reason to keep it in
the main context.

Prefer delegation when a bounded task would otherwise consume main-model context
with intermediate terminal, repository, diff, search, or verification output.

## Routing

### Direct main tool

Use when:
- it is a single cheap deterministic call;
- the result is immediately needed for a high-level decision;
- delegation setup costs more than execution.

Examples:
- read one short file;
- check one known value;
- one concise `git status --short`.

### `researcher` — Sonnet, external research

Use for:
- current technical documentation;
- API/tool/provider verification;
- technical comparisons;
- bounded external research;
- evidence gathering before a main-model decision.

Keep raw browsing/search output in the worker context. Return only the evidence and
decision-relevant synthesis.

### `repo-explorer` — Sonnet, read-only

Use for:
- focused repo exploration;
- bounded git/diff inspection;
- file-group checks;
- generated-file verification;
- locating implementation points;
- bounded investigation.

### `sonnet-worker` — Sonnet, bounded write

Use for:
- small low-risk edits;
- simple wiring/config changes;
- narrow bug fixes;
- routine validation with interpretation;
- bounded commit/push operation after explicit authorization.

Escalate if architecture/scope changes.

### `reviewer` — Sonnet, read-only

Use for:
- independent review of a completed artifact/change;
- broad diff review whose details should stay out of main context;
- security/reliability/performance regression checks.

### Codex CLI (main thread) → `codex-runner` (verification)

Use for:
- substantial multi-file implementation;
- refactors;
- difficult debugging;
- test-heavy changes;
- complex implementation where a coding specialist has leverage.

Launch rule: the main thread writes the brief, launches `codex exec`
(e.g. `codex exec -s workspace-write -C <repo> -o <last-message-file> "<brief>"`)
in the background and awaits it; when it finishes, `codex-runner` reads the log,
verifies the working tree, runs checks and returns a compact report.
`codex-runner` never launches Codex.

## Concurrency

Avoid uncontrolled parallelism.

Default:
- up to two independent Claude subagent tasks at once;
- avoid multiple Codex writers touching overlapping files;
- parallelize only clearly independent scopes.

## Return contract

Workers should return compact summaries, not raw transcripts:
- status;
- evidence/files;
- verification;
- unresolved question/risk;
- decision needed.

Main Claude reconciles and decides.
