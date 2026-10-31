# Brain — Vault Protocol

This vault is the user's durable memory across projects. This file is the
vault's single entry point: whichever agent you are, read it before you start
working with this folder.

This protocol is agent-agnostic. It is not tied to a particular product,
runtime, or subscription. A hook that injects context automatically is only a
convenience; the vault explains itself without any hook.

## Reading order at session start

1. This file (`VAULT.md`).
2. `850-Memory/CORE.md` — durable working preferences.
3. `850-Memory/LAST_SESSION.md` — where we left off.
4. `850-Memory/THREADS.md` — open work threads.
5. If there is an active project: the project's own durable docs.

Do **not** auto-load anything beyond this. `500-Knowledge`, `600-Arsenal`,
`000-Inbox`, `900-Archive` and `JOURNAL.md` are read only when needed right
now. Progressive disclosure is the rule; dumping the whole vault into context
is forbidden.

## Source priority

When sources conflict, in order:

1. Current local repo / working tree state
2. Current durable state and decision files inside the project
3. This vault (global continuity)
4. The agent's own local/automatic memory
5. Old session history

Global memory never overrides current repo truth. If the vault and the repo
disagree, verify local state first, then fix the vault.

## Structure

| Folder | Contents |
|---|---|
| `000-Inbox/` | Raw capture. Not permanent; processed into its proper place on request. |
| `100-Command-Center/` | `DASHBOARD.md` — navigation surface for humans. |
| `200-Goals/` | Goals and direction. |
| `300-Projects/` | `PROJECT_INDEX.md` — where projects live and their status. Project source is never copied here. |
| `500-Knowledge/` | Long-lived technical notes, research summaries. |
| `600-Arsenal/` | Reusable workflows, commands, tools, and working-model notes. |
| `800-Mind/` | Working style, thinking habits, personal context. |
| `850-Memory/` | The continuity core. See below. |
| `900-Archive/` | Closed work and retired documents. |
| `Templates/` | Note templates. |
| `runtime/` | Optional portable working layer: hooks, tools, agents (memory-keeper) and tests (shipped separately). |

## Continuity core — `850-Memory/`

| File | Role | How it is written |
|---|---|---|
| `CORE.md` | High-signal, long-lived working preferences | Rarely, when a rule changes |
| `LAST_SESSION.md` | Short summary of the last meaningful checkpoint | **Overwritten**, not accumulated |
| `THREADS.md` | Only active / paused / waiting work | Updated as status changes |
| `JOURNAL.md` | Decisions that answer "why did we do it this way?" | Appended only when noteworthy |
| `MEMORY_PROTOCOL.md` | Detailed reference for writing discipline | Read when writing memory |

These file names are fixed. Renaming them breaks runtimes that inject them
automatically.

## When to write

Updating memory is part of the work when any of these happens:

- a milestone/phase is completed
- an important decision is made
- a blocker or risk changes
- the next concrete step changes
- the session is about to close

Order: verify local state first → project durable docs → `LAST_SESSION.md` →
`THREADS.md` (if changed) → `PROJECT_INDEX.md` (if changed) → `JOURNAL.md` (if
there is a long-lived decision) → `500-Knowledge/` (if there is a reusable
lesson) → health check (e.g. `runtime/tools/vault-doctor.py`, if installed) →
commit + push.

Vault writes are done by the cheap `memory-keeper` agent
(`runtime/agents/memory-keeper.md`), not the main thread; the main thread gives
it a short brief. A runtime that does not support agents follows this order
itself.

See `850-Memory/MEMORY_PROTOCOL.md` for detail.

## Conventions

- Every note starts with YAML frontmatter: `title`, `created`, `modified`,
  `type`, `status`, `tags`. Template: `Templates/Note.md`.
- Notes link to each other with `[[wikilink]]`.
- Status vocabulary: 🟢 active · 🟡 in progress · 🔴 blocked · ⚪ paused
- Folder names are plain ASCII. No emoji — they need quoting in shell commands
  every time.
- Dates are absolute (`2026-08-21`); never write "yesterday" or "last week".

## Never written

- secrets, API keys, tokens, cookies, passwords, SSH keys
- conversation transcripts, raw tool/log dumps, full diffs
- transient debug noise
- unverified speculation presented as fact
- copies of project source code

## Runtime

The vault can carry its own working layer under `runtime/`: the continuity hook
(`brain-memory.py`), tools, agent definitions (memory-keeper) and tests.
Counterparts under `~/.claude` are symlinks to it, so there is a single
source. Hook state lives in `~/.claude/brain-state`.

The hook is optional — any agent that follows the reading order above can use
the vault fully. The hook only automates it.

## Syncing

If the vault is a git repository, sync it through git:

- At session start: the hook runs `git pull --ff-only` (skipped when the
  branch has no upstream); it never merges or rewrites local work
- At session end: memory-keeper commits its changes, runs `git pull --rebase`,
  then pushes (commit first: a rebase will not run over unstaged edits)

The hook can warn at session start if there is unpushed memory.

Project repositories and their `docs/ai/` documents are **outside** this sync;
`docs/ai/` follows each project's visibility rules and is carried between
machines by the user.
