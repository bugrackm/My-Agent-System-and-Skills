# Codex CLI Policy

Codex is a coding specialist, not the project manager.

## Authentication

Subscription auth only; billing and secret rules are in the global CLAUDE.md.

## Invocation

The main thread launches `codex exec` (in the background, e.g.
`codex exec -s workspace-write -C <repo> -o <last-message-file> "<brief>"`) and
awaits it. Never
delegate the launch to a subagent: a subagent cannot outlive its own turn, so a
long Codex run dies or is lost with it. When the run finishes, hand the log and
working tree to `codex-runner`, which verifies and returns a compact report so
Codex transcript/tool output does not fill main Opus context.

Before first use on a machine/version, the main thread may inspect:

`codex exec --help`

Use current CLI syntax rather than assuming stale flags.

Permission principle:
- review/analysis: read-only sandbox where possible;
- approved implementation: `--sandbox workspace-write`;
- never `danger-full-access` for normal project work.

## CODEX_BRIEF

A good brief is self-contained:
- objective;
- current milestone;
- exact scope;
- relevant paths/context;
- constraints/decisions to preserve;
- acceptance criteria;
- tests/checks;
- explicit non-goals;
- git permission (none unless authorized).

Do not dump the whole project history.

## After Codex

The runner:
- checks changed files/diff summary;
- runs/records relevant verification;
- returns a compact result.

Main Claude:
- reconciles result with architecture and durable state;
- asks for/uses independent review when needed;
- accepts only after quality gates.
