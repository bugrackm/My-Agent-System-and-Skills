# AGENTS.md: installation guide for AI agents

You are an AI coding agent (Claude Code or similar) helping a user install parts of this repo into their own Claude Code setup. Follow these steps in order. The user may speak Turkish or English; answer in their language.

## Ground rules

- **Ask before you act.** First explain the three parts in one line each, then ask which ones the user wants:
  - **brain:** persistent memory.
  - **agents:** orchestration subagents and a global `CLAUDE.md`.
  - **skills:** `game-dev-director` and the `context-meter` plugin.
- **Back up before you change anything:** `~/.claude/settings.json`, `~/.claude/CLAUDE.md`, `~/.claude/agents/`.
- **Never overwrite.**
  - If a target file already exists, show the user a diff and ask.
  - `settings.json` is only ever *merged*, via `brain/merge-settings.py`. Never rewrite it by hand.
  - `CLAUDE.md` is only ever *appended to* or merged section by section, with the user's approval.
- **Privacy.** The brain vault the user creates will hold personal data. If you create a git remote for it, it must be **private** (`gh repo create <name> --private`). Never push the vault to a public repo.
- **No paid APIs.** Don't set up API keys. Codex CLI, if wanted, signs in with the user's ChatGPT subscription (`codex login`), and the user does that themselves.
- **Don't run interactive logins yourself.** For `codex login` or `gh auth login`, ask the user to run them (in Claude Code, by typing `! <command>`).
- **Platform.** `brain/` targets Linux and macOS shells. On native Windows, install `brain-windows/` instead (PowerShell commands, copies instead of symlinks). If the user wants one brain shared across Windows, Linux and macOS, have them run Claude Code inside WSL and install `brain/` there. Never set up one vault shared between `brain-windows/` and `brain/`; see `brain-windows/README.md`. The agents and skills parts need adapted paths on Windows.

## Steps

Clone the repo to a stable location (e.g. `~/src/My-Agent-System-and-Skills`) and run every command from its root.

1. **Brain** (if chosen): follow [`brain/INSTALL.md`](brain/INSTALL.md#english) steps 1–8 in order. On native Windows, follow [`brain-windows/INSTALL.md`](brain-windows/INSTALL.md#english) instead; the same sub-rules apply (its default vault path is `%USERPROFILE%\Brain`).
   - Ask the user for the vault path; the default is `~/Documents/Brain`.
   - Stop if that path already exists.
   - Run `merge-settings.py --dry-run` first and show the user the output.
   - In step 6, ask the user the questions needed to fill `850-Memory/CORE.md`, or leave it for them.
   - Step 7 (private git remote) is optional; ask.
2. **Agents** (if chosen): follow [`agents/INSTALL.md`](agents/INSTALL.md#english).
   - Ask which agents to install.
   - Skip `codex-runner` unless the user wants Codex CLI.
   - For `CLAUDE.md`: if one exists, propose the sections to add and get approval. If the brain isn't installed, drop the whole "Brain (optional)" section (the vault and memory-keeper rules live only there); keep the other sections.
3. **Skills** (if chosen): follow [`skills/INSTALL.md`](skills/INSTALL.md#english).
   - `game-dev-director` is copied (or symlinked) into `~/.claude/skills/`.
   - `context-meter` is a plugin. Tell the user to run the `/plugin install …` line themselves, since slash commands are typed by the user.

## Verify and report

- Brain: `vault-doctor.py` prints `vault-doctor: OK`, and the runtime tests pass.
- Agents: tell the user to open a new session and run `/agents`.
- Skills: tell the user to open a new session and try `/game-dev-director`.
- Finish with a short summary for the user:
  - what was installed, and where
  - which files were changed, and where their backups are
  - anything they still need to do themselves (logins, `/plugin install`, filling `CORE.md`)
  - a reminder that changes take effect in a **new** Claude Code session
