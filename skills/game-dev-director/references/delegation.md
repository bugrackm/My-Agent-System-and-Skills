# Delegation in Game Projects

The routing rules are in the global CLAUDE.md. This page only adds what tends
to come up in game work.

- Most game decisions need the conversation: what is fun, what to cut, which
  gate we are at. Keep them in the main thread.
- Good delegation targets: a Godot or engine API check (`researcher`, told to
  open the docs); locating where a mechanic lives across scenes and scripts
  (`repo-explorer`); an independent review of a finished feature branch
  (`reviewer`); a routine export or config change (`sonnet-worker`); a
  multi-file mechanic implementation or hard bug (Codex, launched by the main
  thread, verified by `codex-runner`).
- Do not delegate feel. An agent cannot judge whether a jump feels good; that
  needs the user on a device.
- No overlapping writers: never two Codex runs or a Codex run and a
  `sonnet-worker` on the same files at once.

## Brief contract

Every brief states goal, scope, out-of-scope, the files or docs to start from,
acceptance checks, git permission (none unless the user authorized it), and what
to return: status, evidence, verification, open risks, decision needed. Workers
return summaries, not transcripts. Read-only agents do not load CLAUDE.md, so
restate any rule they need.
