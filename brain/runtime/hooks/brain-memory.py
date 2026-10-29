#!/usr/bin/env python3
"""
Brain <-> Claude Code continuity hook.

Expected install layout: ``$BRAIN_HOME/runtime/{hooks,tools,agents}``, with
``~/.claude/hooks/brain-memory.py`` and ``~/.claude/agents/memory-keeper.md``
symlinked (or copied) from that runtime directory.

Events:
  session-start
  prompt
  stop
  session-end

Reads Claude hook JSON from stdin. It never edits Brain or project durable
documents. It only:
- fast-forwards the vault from its remote at SessionStart (--ff-only, so
  nothing local is merged or rewritten),
- injects compact continuity at SessionStart,
- nudges background memory-keeper delegation after unsaved stretches and compaction,
- surfaces transcript recovery and runtime configuration drift,
- tracks whether canonical durable state was updated,
- leaves a reflection marker if a meaningful session ends without such an update.

Global (Brain) and project (repo) durable state are tracked separately: a
session that updates repo docs but leaves global memory behind is the common
way this system rots, and conflating the two hides it. SessionStart also
labels global memory as stale when the repo has newer commits, and reports a
missing Brain path instead of degrading silently.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HOME = Path.home()
BRAIN = Path(os.environ.get("BRAIN_HOME") or (Path.home() / "Documents" / "Brain")).expanduser()
MEM = BRAIN / "850-Memory"
STATE = HOME / ".claude" / "brain-state"
SESSIONS = STATE / "sessions"
REFLECTIONS = STATE / "needs-reflection"

GLOBAL_FILES = {
    "core": MEM / "CORE.md",
    "last": MEM / "LAST_SESSION.md",
    "threads": MEM / "THREADS.md",
    "journal": MEM / "JOURNAL.md",
}

PROJECT_NAMES = ("HANDOFF.md", "PROJECT_CONTEXT.md", "CURRENT_TASK.md")


def read_input() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def safe_id(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value or "unknown")
    return value[:160] or "unknown"


def state_path(session_id: str) -> Path:
    return SESSIONS / f"{safe_id(session_id)}.json"


def now() -> float:
    return time.time()


def file_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def git_root(cwd: Path) -> Path:
    try:
        p = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
        if p.returncode == 0 and p.stdout.strip():
            return Path(p.stdout.strip()).resolve()
    except Exception:
        pass
    try:
        return cwd.resolve()
    except Exception:
        return cwd


def project_docs(root: Path) -> dict[str, Path]:
    docs_ai = root / "docs" / "ai"
    result: dict[str, Path] = {}
    for name in PROJECT_NAMES:
        p = docs_ai / name
        if not p.exists():
            p = root / name
        if p.exists():
            result[name] = p
    return result


def compact_text(path: Path, max_chars: int, max_lines: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lines = text.splitlines()[:max_lines]
    out = "\n".join(lines).strip()
    if len(out) > max_chars:
        out = out[:max_chars].rstrip() + "\n[…truncated by continuity hook…]"
    return out


def active_threads(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    # Prefer an "Active" section if present; otherwise keep a compact front slice.
    # The section ends at the next heading of the same or shallower level, so a
    # document title ("# Active Threads") keeps its nested "## <project>" blocks
    # instead of terminating on the first one.
    start = None
    level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,3})\s+Active\b", line, re.I)
        if m:
            start = i
            level = len(m.group(1))
            break

    if start is None:
        chosen = lines[:35]
    else:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            m2 = re.match(r"^(#{1,6})\s+\S", lines[j])
            if m2 and len(m2.group(1)) <= level:
                end = j
                break
        chosen = lines[start:end]

    out = "\n".join(chosen).strip()
    return out[:1800]


def snapshot(root: Path) -> dict[str, float]:
    docs = project_docs(root)
    snap = {f"global:{k}": file_mtime(v) for k, v in GLOBAL_FILES.items()}
    for name, path in docs.items():
        snap[f"project:{name}"] = file_mtime(path)
    return snap


def changed_since(snap: dict[str, float], root: Path, prefix: str = "") -> bool:
    """Did tracked files change? Restrict to one layer with `prefix`.

    Layers must be checked separately. A single combined check reports success
    as soon as either layer moves, so diligently updated repo docs mask global
    memory that has not been touched in weeks.
    """
    current = snapshot(root)
    keys = set(snap) | set(current)
    for k in keys:
        if prefix and not k.startswith(prefix):
            continue
        if current.get(k, 0.0) > snap.get(k, 0.0) + 0.0001:
            return True
    return False


def newest_commit_time(root: Path) -> float:
    try:
        p = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%ct"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
        if p.returncode == 0 and p.stdout.strip():
            return float(p.stdout.strip())
    except Exception:
        pass
    return 0.0


_commit_ts_cache: dict[str, float] = {}


def staleness_note(root: Path, path: Path) -> str:
    """Flag global memory the repo has already moved past.

    Priority rules keep stale global memory from being acted on, but unlabelled
    stale text still costs context and attention every session. Comparing it to
    the newest commit turns that into a visible, self-clearing signal.
    """
    key = str(root)
    if key not in _commit_ts_cache:
        _commit_ts_cache[key] = newest_commit_time(root)
    commit_ts = _commit_ts_cache[key]
    mem_ts = file_mtime(path)
    if not commit_ts or not mem_ts or commit_ts <= mem_ts + 3600:
        return ""
    days = int((commit_ts - mem_ts) // 86400)
    age = f"{days} day(s) older" if days >= 1 else "older"
    return (
        f"  ⚠ STALE — this is {age} than the newest commit in `{root.name}`. "
        "Repo-local durable state is authoritative; update this file at the next checkpoint."
    )


def vault_pull() -> str:
    """Fast-forward the vault from the remote before continuity is read.

    Without this, a session on one machine resumes from memory that another
    machine has already moved past, and its own commits later diverge from
    the remote.
    Only --ff-only runs, so local work is never merged or rewritten here; a
    divergence is reported instead. The network sits on the hook path, so
    the pull is capped well inside the hook timeout and never prompts.
    """
    if not (BRAIN / ".git").exists():
        return ""
    try:
        # No upstream (no remote, or branch not tracking one): nothing to pull.
        up = subprocess.run(
            ["git", "-C", str(BRAIN), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            capture_output=True, text=True, timeout=2,
        )
    except Exception:
        return ""
    if up.returncode != 0:
        return ""
    env = dict(
        os.environ,
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=3",
    )
    try:
        r = subprocess.run(
            ["git", "-C", str(BRAIN), "pull", "--no-rebase", "--ff-only", "--quiet"],
            capture_output=True, text=True, timeout=5, env=env,
        )
    except subprocess.TimeoutExpired:
        return (
            "[Brain sync warning]\n"
            "Vault pull timed out (the network may be unavailable). Continuity is "
            "coming from this machine's local copy; another machine's latest session may be missing."
        )
    except Exception:
        return ""
    if r.returncode == 0:
        return ""
    try:
        counts = subprocess.run(
            ["git", "-C", str(BRAIN), "rev-list", "--left-right", "--count", "HEAD...@{u}"],
            capture_output=True, text=True, timeout=2,
        ).stdout.split()
        ahead, behind = int(counts[0]), int(counts[1])
    except Exception:
        ahead = behind = 0
    if ahead and behind:
        detail = (
            f"local and remote histories have diverged ({ahead} local, {behind} remote commits). "
            "Run `git pull --rebase` before writing to the vault."
        )
    else:
        lines = r.stderr.strip().splitlines()
        errors = [l for l in lines if l.startswith(("fatal:", "error:"))]
        reason = (errors or lines or ["unknown error"])[0]
        detail = f"vault pull failed: {reason}"
    return (
        "[Brain sync warning]\n"
        + detail
        + " Continuity is coming from this machine's local copy."
    )


def vault_sync_note() -> str:
    """Warn when vault memory has not reached the remote yet.

    Machines that share this vault through git cannot see memory that is
    only committed locally — or not committed at all. A session starting
    there would silently resume from stale continuity. Only local checks run
    here; vault_pull() has already talked to the remote.
    """
    if not (BRAIN / ".git").exists():
        return ""

    def run(args: list[str]) -> str:
        try:
            r = subprocess.run(
                ["git", "-C", str(BRAIN)] + args,
                capture_output=True, text=True, timeout=3,
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""

    bits = []
    if run(["status", "--porcelain"]):
        bits.append("there are uncommitted changes")
    ahead = run(["rev-list", "--count", "@{u}..HEAD"])
    if ahead.isdigit() and int(ahead) > 0:
        bits.append(f"{ahead} commit(s) have not been pushed")
    if not bits:
        return ""
    return (
        "[Brain sync warning]\n"
        "The vault repository has " + " and ".join(bits) + ". Memory written on "
        "this machine will not reach another machine; commit and push at session end."
    )


def load_state(session_id: str) -> dict[str, Any]:
    p = state_path(session_id)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(session_id: str, data: dict[str, Any]) -> None:
    SESSIONS.mkdir(parents=True, exist_ok=True)
    state_path(session_id).write_text(json.dumps(data, indent=2), encoding="utf-8")


def matching_reflections(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    REFLECTIONS.mkdir(parents=True, exist_ok=True)
    matches: list[tuple[Path, dict[str, Any]]] = []
    cutoff = now() - 7 * 24 * 3600
    for p in sorted(REFLECTIONS.glob("*.json"), key=lambda x: file_mtime(x), reverse=True):
        if file_mtime(p) < cutoff:
            try:
                p.unlink()
            except OSError:
                pass
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("kind") == "global" or data.get("project_root") == str(root):
                matches.append((p, data))
        except Exception:
            continue
    return matches[:3]


def missing_hook_events() -> list[str]:
    try:
        template = json.loads((BRAIN / "runtime/settings.template.json").read_text())
        live = json.loads((HOME / ".claude/settings.json").read_text())
        missing = []
        for event, groups in template.get("hooks", {}).items():
            commands = {h["command"] for g in groups for h in g.get("hooks", [])
                        if h.get("type") == "command" and "command" in h}
            installed = {h["command"] for g in live.get("hooks", {}).get(event, [])
                         for h in g.get("hooks", []) if "command" in h}
            if commands - installed:
                missing.append(event)
        return missing
    except Exception:
        return []


def refresh_global_write(data: dict[str, Any]) -> None:
    root = Path(data["project_root"])
    snap = data.setdefault("snapshot", {})
    if changed_since(snap, root, "global:"):
        snap.update({f"global:{k}": file_mtime(v) for k, v in GLOBAL_FILES.items()})
        data["prompts_at_last_write"] = int(data.get("prompt_count", 0))
        data["stop_reminded"] = False
        # Preserve session-wide evidence after advancing the stretch baseline.
        data["global_updated"] = True


def emit_context(event: str, text: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))


def handle_session_start(inp: dict[str, Any]) -> None:
    sid = str(inp.get("session_id") or f"pid-{os.getpid()}")
    cwd = Path(str(inp.get("cwd") or os.getcwd())).expanduser()
    root = git_root(cwd)
    source = str(inp.get("source") or "startup")
    old = load_state(sid)

    # Pull before the snapshot: files arriving from the other machine must not
    # count as this session having updated durable state. Compaction is the
    # same session, so it does not pull again.
    pull_note = "" if source == "compact" else vault_pull()

    # Compaction is still the same logical session. Do not reset its counters.
    if old and source == "compact":
        data = old
    else:
        data = {
            "session_id": sid,
            "start_time": now(),
            "prompt_count": 0,
            "prompts_at_last_write": 0,
            "stop_reminded": False,
            "project_root": str(root),
            "snapshot": snapshot(root),
        }

    data["transcript_path"] = inp.get("transcript_path") or data.get("transcript_path", "")
    if source == "compact":
        data["stop_reminded"] = False
    save_state(sid, data)
    parts: list[str] = []
    if source == "compact":
        parts.append(
            "[Brain compaction checkpoint]\nContext was just compacted. If the "
            "compacted span contained durable developments not yet in memory, brief "
            "memory-keeper now in the background."
        )
    else:
        missing = missing_hook_events()
        if missing:
            parts.append(
                "[Brain runtime drift]\nMissing events: " + ", ".join(missing) +
                ". Merge the hooks entries from runtime/settings.template.json into "
                "~/.claude/settings.json (merge, never overwrite other keys)."
            )

    # A missing vault must be loud. The hook fails open by design, so without
    # this the only symptom of a moved/renamed Brain is continuity quietly
    # disappearing, which reads like "there was nothing to say".
    if not MEM.is_dir():
        parts.append(
            "[Brain health warning]\n"
            f"Global memory directory not found at `{MEM}`. Continuity injection is "
            "degraded for this session. Verify the vault path (or set BRAIN_HOME) "
            "before treating missing global context as 'no prior work'."
        )

    refs = [] if source == "compact" else matching_reflections(root)
    for p, data in refs:
        transcript = data.get("transcript_path")
        if data.get("kind") == "global" and transcript and Path(transcript).is_file():
            parts.append(
                "[Brain recovery required]\n"
                f"Previous session `{str(data.get('session_id', 'unknown'))[:12]}` "
                f"(`{data.get('project_root', 'unknown')}`, ended `{data.get('ended_at', 'unknown')}`) "
                "ended without a vault memory write; launch memory-keeper in the "
                f"background in recovery mode with transcript `{transcript}`; "
                "do not interrupt the user about it."
            )
            p.unlink(missing_ok=True)
            continue
        detail = ""
        if data.get("global_updated") is False and data.get("project_updated") is False:
            detail = " Neither repo-local docs nor Brain global memory were written."
        elif data.get("project_updated") is False:
            detail = " Repo-local durable docs were not written."
        parts.append(
            "[Brain continuity warning]\n"
            "A previous meaningful session for this project appears to have ended "
            "without updating canonical durable state." + detail + " Reconcile "
            "repo-local state before relying on memory."
        )
        try:
            p.unlink()
        except OSError:
            pass

    if pull_note:
        parts.append(pull_note)

    sync = vault_sync_note()
    if sync:
        parts.append(sync)

    last = compact_text(GLOBAL_FILES["last"], 3000, 55)
    if last:
        parts.append(
            "[Brain — Last Session]"
            + staleness_note(root, GLOBAL_FILES["last"])
            + "\n"
            + last
        )

    threads = active_threads(GLOBAL_FILES["threads"])
    if threads:
        parts.append(
            "[Brain — Active Threads]"
            + staleness_note(root, GLOBAL_FILES["threads"])
            + "\n"
            + threads
        )

    docs = project_docs(root)
    handoff = docs.get("HANDOFF.md")
    if handoff:
        rel = os.path.relpath(handoff, root)
        handoff_excerpt = compact_text(handoff, 3600, 65)
        parts.append(
            f"[Project durable state — {root.name}]\n"
            f"Authoritative handoff: `{rel}`\n"
            "Recovery order: HANDOFF → PROJECT_CONTEXT → CURRENT_TASK → "
            "`git status --short` → only relevant source files.\n"
            "Repo-local state overrides stale Brain/native memory.\n\n"
            + handoff_excerpt
        )
    else:
        parts.append(
            f"[Project detection]\nCurrent project root: `{root}`.\n"
            "No HANDOFF.md was found in `docs/ai/` or repo root. Do not invent "
            "project state from global memory."
        )

    parts.append(
        "[Brain memory policy]\n"
        f"The vault at `{BRAIN}` is the single source of durable memory; its "
        f"protocol is `{BRAIN / 'VAULT.md'}`. Project-local durable docs are "
        "project truth and outrank the vault. Do not write lasting facts to "
        f"per-project agent memory. Read `{GLOBAL_FILES['core']}` when deeper "
        "cross-project context is relevant. Preserve milestone names exactly."
    )

    emit_context("SessionStart", "\n\n".join(parts))


def handle_prompt(inp: dict[str, Any]) -> None:
    sid = str(inp.get("session_id") or f"pid-{os.getpid()}")
    data = load_state(sid)
    if not data:
        cwd = Path(str(inp.get("cwd") or os.getcwd())).expanduser()
        root = git_root(cwd)
        data = {
            "session_id": sid,
            "start_time": now(),
            "prompt_count": 0,
            "prompts_at_last_write": 0,
            "stop_reminded": False,
            "project_root": str(root),
            "snapshot": snapshot(root),
        }
    refresh_global_write(data)
    data["transcript_path"] = inp.get("transcript_path") or data.get("transcript_path", "")
    data["prompt_count"] = int(data.get("prompt_count", 0)) + 1
    save_state(sid, data)

    count = data["prompt_count"]
    if count in (12, 24):
        emit_context(
            "UserPromptSubmit",
            "[Brain checkpoint reminder] This session is getting long. If a "
            "meaningful development checkpoint has occurred, keep repo-local "
            "HANDOFF/CURRENT_TASK/DECISIONS current before changing milestone or "
            "ending. Brief memory-keeper in the background with durable developments; "
            "keep global memory compact and do not dump tool logs into it."
        )


def handle_stop(inp: dict[str, Any]) -> None:
    if inp.get("stop_hook_active"):
        return
    sid = str(inp.get("session_id") or f"pid-{os.getpid()}")
    data = load_state(sid)
    if not data:
        return
    data["transcript_path"] = inp.get("transcript_path") or data.get("transcript_path", "")
    refresh_global_write(data)
    stretch = int(data.get("prompt_count", 0)) - int(data.get("prompts_at_last_write", 0))
    remind = stretch >= 4 and not data.get("stop_reminded", False)
    if remind:
        data["stop_reminded"] = True
    # Persist before emitting so a failed write cannot cause repeated blocks.
    save_state(sid, data)
    if remind:
        print(json.dumps({"decision": "block", "reason": (
            "This session has unsaved durable development candidates. If anything "
            "durable happened (decision, finished step, changed next step, new learning), "
            "launch the memory-keeper agent in the background with a compact brief. "
            "If nothing durable happened, just end the turn. Do not mention vault "
            "bookkeeping to the user."
        )}))


def handle_session_end(inp: dict[str, Any]) -> None:
    sid = str(inp.get("session_id") or f"pid-{os.getpid()}")
    data = load_state(sid)
    if not data:
        return

    prompts = int(data.get("prompt_count", 0))
    root = Path(str(data.get("project_root") or inp.get("cwd") or os.getcwd()))
    snap = data.get("snapshot") or {}

    project_updated = changed_since(snap, root, "project:")
    global_updated = bool(data.get("global_updated")) or changed_since(snap, root, "global:")

    # Roots without durable docs must not create spurious project reminders.
    if prompts >= 4 and (not global_updated or (project_docs(root) and not project_updated)):
        REFLECTIONS.mkdir(parents=True, exist_ok=True)
        marker = {
            "session_id": sid,
            "transcript_path": inp.get("transcript_path") or data.get("transcript_path", ""),
            "kind": "global" if not global_updated else "project",
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "project_root": str(root),
            "prompt_count": prompts,
            "reason": inp.get("reason", "other"),
            "project_updated": project_updated,
            "global_updated": global_updated,
            "message": "Meaningful session ended without a detected canonical durable-state write.",
        }
        p = REFLECTIONS / f"{int(now())}-{safe_id(root.name)}-{safe_id(sid)}.json"
        p.write_text(json.dumps(marker, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        state_path(sid).unlink()
    except OSError:
        pass


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    event = {
        "SessionStart": "session-start",
        "UserPromptSubmit": "prompt",
        "Stop": "stop",
        "SessionEnd": "session-end",
    }.get(event, event)
    inp = read_input()

    try:
        STATE.mkdir(parents=True, exist_ok=True)
        if event == "session-start":
            handle_session_start(inp)
        elif event == "prompt":
            handle_prompt(inp)
        elif event == "stop":
            handle_stop(inp)
        elif event == "session-end":
            handle_session_end(inp)
        else:
            print(f"Unknown event: {event}", file=sys.stderr)
            return 0
    except Exception as exc:
        # Hooks should fail open rather than break Claude Code sessions.
        print(f"brain-memory hook error: {exc}", file=sys.stderr)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

