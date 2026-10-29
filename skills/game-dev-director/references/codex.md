# Codex CLI Policy

Codex is a coding specialist, not the project manager.

## Authentication

Use the user's existing Codex/ChatGPT subscription authentication.

Never:
- create/use an OpenAI API key for this workflow without explicit user request;
- switch billing/auth mode silently;
- expose auth files/tokens.

## Invocation

Launch rule: the main thread writes the brief, launches `codex exec`
(e.g. `codex exec -s workspace-write -C <repo> -o <last-message-file> "<brief>"`)
in the background and awaits it; when it finishes, `codex-runner` reads the log,
verifies the working tree, runs checks and returns a compact report.
`codex-runner` never launches Codex.
This keeps Codex transcript/tool output out of main Opus context.

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
