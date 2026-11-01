# Codex CLI

Optional helper for large, self-contained implementation. Subscription login
only (see global CLAUDE.md).

- The main thread launches `codex exec` in the background and awaits it; a
  subagent cannot outlive its turn, so never delegate the launch. Afterwards
  `codex-runner` can verify the tree and return a compact report.
- Check `codex exec --help` for current flags. Use `--sandbox workspace-write`
  for implementation; never `danger-full-access`.
- Brief (`templates/CODEX_BRIEF.md`): objective, relevant paths, what to
  preserve, acceptance checks, non-goals, git permission (none unless given).
- Review the result yourself before accepting it.
