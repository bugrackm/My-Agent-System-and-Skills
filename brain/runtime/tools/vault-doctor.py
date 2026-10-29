#!/usr/bin/env python3
"""Read-only checks for vault continuity, links, secrets and runtime health."""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess

SECRET = re.compile(r"sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
EXCLUDED = {".git", ".obsidian", ".trash", "runtime", "Templates", "000-Inbox"}
ROOT_DOCS = {"README.md", "VAULT.md", "AGENTS.md", "CLAUDE.md"}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def run_git(vault: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(["git", "-C", str(vault)] + args, capture_output=True,
                                text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def without_code(text: str) -> str:
    lines = []
    fence = ""
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
            continue
        if not fence:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.S)


def runtime_findings(vault: Path) -> list[str]:
    claude = Path.home() / ".claude"
    findings = []
    try:
        template = json.loads(read(vault / "runtime/settings.template.json"))
        live = json.loads(read(claude / "settings.json"))
        for event, groups in template.get("hooks", {}).items():
            commands = {h["command"] for g in groups for h in g.get("hooks", [])
                        if h.get("type") == "command" and "command" in h}
            installed = {h["command"] for g in live.get("hooks", {}).get(event, [])
                         for h in g.get("hooks", []) if "command" in h}
            if commands - installed:
                findings.append(f"missing hook event {event}; merge template hooks into ~/.claude/settings.json")
    except (ValueError, TypeError, AttributeError):
        pass
    # Copies and symlinks are both fine; only the two installed entry points must exist.
    for name in ("hooks/brain-memory.py", "agents/memory-keeper.md"):
        if not (claude / name).is_file():
            findings.append(f"~/.claude/{name} is missing; copy or symlink it from {vault / 'runtime'}")
    return findings


def check(vault: Path, today: date) -> list[tuple[str, str, str]]:
    issues: list[tuple[str, str, str]] = []

    def warn(area: str, message: str) -> None:
        issues.append(("WARN", area, message))

    files = []
    # Do not follow directory symlinks outside the vault or into cycles.
    for directory, dirs, names in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        files.extend(Path(directory) / name for name in sorted(names))
    notes = [p for p in files if p.suffix.lower() == ".md"]
    basenames = {p.stem.casefold() for p in notes}
    relative = {p.relative_to(vault).with_suffix("").as_posix().casefold() for p in notes}
    for path in notes:
        rel = path.relative_to(vault)
        if any(part in EXCLUDED for part in rel.parts[:-1]) or path.name == "README.md":
            continue
        if len(rel.parts) == 1 and path.name in ROOT_DOCS:
            continue
        text = read(path)
        if "850-Memory" not in rel.parts[:-1]:
            front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
            if not front or not re.search(r"^title\s*:", front.group(1), re.M):
                warn("frontmatter", f"{rel}: missing opening YAML block with title")
        for match in re.finditer(r"\[\[([^\]\n]+)\]\]", without_code(text)):
            target = re.split(r"[|#]", match.group(1), maxsplit=1)[0].strip()
            if not target:
                continue
            target = re.sub(r"\.md$", "", target, flags=re.I).casefold()
            if target not in basenames and target not in relative:
                warn("wikilinks", f"{rel}: unresolved [[{target}]]")
    threads = read(vault / "850-Memory/THREADS.md")
    for entry in re.split(r"^## ", threads, flags=re.M)[1:]:
        status = re.search(r"Status:([^\n]*)", entry)
        touched = re.search(r"Last touched:\s*(\d{4}-\d{2}-\d{2})", entry)
        if status and touched and any(s in status.group(1) for s in ("🟢", "🟡")):
            try:
                if (today - date.fromisoformat(touched.group(1))).days > 30:
                    warn("threads", f"{entry.splitlines()[0]}: last touched {touched.group(1)}")
            except ValueError:
                pass
    last = read(vault / "850-Memory/LAST_SESSION.md")
    if len(last) > 3000 or len(last.splitlines()) > 55:
        warn("last_session size", "850-Memory/LAST_SESSION.md exceeds 3000 chars or 55 lines")
    if len(read(vault / "850-Memory/JOURNAL.md").splitlines()) > 250:
        warn("journal size", "archive older entries to 900-Archive/journal-YYYY.md")
    if run_git(vault, ["status", "--porcelain"]):
        warn("git", "uncommitted or untracked changes")
    ahead = run_git(vault, ["rev-list", "--count", "@{u}..HEAD"])
    if ahead.isdigit() and int(ahead):
        warn("git", f"{ahead} commit(s) ahead of upstream")
    for path in files:
        if path.suffix.lower() not in {".md", ".json", ".py", ".toml"}:
            continue
        for number, line in enumerate(read(path).splitlines(), 1):
            if SECRET.search(line):
                issues.append(("ERROR", "secrets", f"{path.relative_to(vault)}:{number}"))
    for message in runtime_findings(vault):
        warn("runtime drift", message)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path(os.environ.get("BRAIN_HOME") or (Path.home() / "Documents" / "Brain")),
    )
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    issues = check(args.vault.expanduser().resolve(), args.today)
    for level, area, message in issues:
        # Even filenames and note titles may contain credentials.
        print(SECRET.sub("[REDACTED]", f"{level} {area}: {message}"))
    print(f"vault-doctor: {len(issues)} issue(s)" if issues else "vault-doctor: OK")
    return int(any(level == "ERROR" for level, _, _ in issues))


if __name__ == "__main__":
    raise SystemExit(main())

