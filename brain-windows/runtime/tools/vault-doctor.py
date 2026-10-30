#!/usr/bin/env python3
"""Read-only checks for Windows vault continuity, links, secrets and runtime health."""

from __future__ import annotations

import argparse
import base64
from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SECRET = re.compile(r"sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
EXCLUDED = {".git", ".obsidian", ".trash", "runtime", "Templates", "000-Inbox"}
ROOT_DOCS = {"README.md", "VAULT.md", "AGENTS.md", "CLAUDE.md"}
EVENT_ARGUMENTS = {
    "SessionStart": "session-start",
    "UserPromptSubmit": "prompt",
    "Stop": "stop",
    "SessionEnd": "session-end",
}
RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}
GIT_ATTRIBUTES = {
    "* text=auto eol=lf",
    "*.md   text eol=lf",
    "*.py   text eol=lf",
    "*.json text eol=lf",
    "*.ps1  text eol=lf",
    "*.sh   text eol=lf",
}


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def run_git(vault: Path, args: list[str]) -> str:
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never",
               GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=3")
    try:
        result = subprocess.run(
            ["git", "-C", str(vault)] + args, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=5, env=env, **kwargs
        )
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


def decode_hook_command(command: object) -> str:
    if not isinstance(command, str):
        return ""
    match = re.search(
        r"(?i)(?:^|\s)-EncodedCommand\s+([A-Za-z0-9+/]+={0,2})(?=\s|$)", command
    )
    if not match:
        return command
    try:
        return base64.b64decode(match.group(1), validate=True).decode("utf-16le")
    except (ValueError, UnicodeDecodeError):
        return command


def hook_installed(groups: object, argument: str) -> bool:
    if not isinstance(groups, list):
        return False
    for group in groups:
        if not isinstance(group, dict):
            continue
        for hook in group.get("hooks", []):
            if not isinstance(hook, dict):
                continue
            command = hook.get("command")
            decoded = decode_hook_command(command)
            if "brain-memory.py" not in decoded:
                continue
            if isinstance(command, str) and decoded != command:
                pattern = rf"\s{re.escape(argument)};\s*exit\s+\$LASTEXITCODE\s*$"
            else:
                pattern = rf"(?:^|\s){re.escape(argument)}\s*$"
            if re.search(pattern, decoded, flags=re.IGNORECASE):
                return True
    return False


def runtime_findings(vault: Path) -> list[str]:
    claude = Path.home() / ".claude"
    findings = []
    try:
        live = json.loads((claude / "settings.json").read_text(encoding="utf-8-sig"))
        for event, argument in EVENT_ARGUMENTS.items():
            if not hook_installed(live.get("hooks", {}).get(event), argument):
                findings.append(f"missing hook event {event}; run merge-settings.py")
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    for name in ("hooks/brain-memory.py", "agents/memory-keeper.md"):
        source = vault / "runtime" / name
        installed = claude / name
        if not installed.is_file():
            findings.append(f"~/.claude/{name} is missing; run update-runtime.py")
            continue
        try:
            if (source.is_file()
                    and source.read_bytes().replace(b"\r\n", b"\n")
                    != installed.read_bytes().replace(b"\r\n", b"\n")):
                findings.append(f"~/.claude/{name} differs from the runtime copy; run update-runtime.py")
        except OSError:
            pass
    return findings


def windows_name_problem(name: str) -> str | None:
    if any(ord(char) < 32 or char in '<>:"|?*' for char in name):
        return "contains a Windows-invalid character"
    if name.endswith((".", " ")):
        return "ends with a dot or space"
    base = name.rstrip(". ").split(".", 1)[0].casefold()
    if base in RESERVED:
        return "uses a reserved Windows device name"
    return None


def check(vault: Path, today: date) -> list[tuple[str, str, str]]:
    issues: list[tuple[str, str, str]] = []

    def warn(area: str, message: str) -> None:
        issues.append(("WARN", area, message))

    files: list[Path] = []
    paths: list[Path] = []
    for directory, dirs, names in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        root = Path(directory)
        paths.extend(root / name for name in dirs)
        current = [root / name for name in sorted(names)]
        files.extend(current)
        paths.extend(current)

    seen: dict[str, Path] = {}
    for path in paths:
        try:
            rel = path.relative_to(vault)
        except ValueError:
            continue
        problem = windows_name_problem(path.name)
        if problem:
            warn("windows paths", f"{rel}: {problem}")
        folded = rel.as_posix().casefold()
        if folded in seen and seen[folded].as_posix() != rel.as_posix():
            warn("windows paths", f"case collision: {seen[folded]} and {rel}")
        else:
            seen[folded] = rel
        if len(rel.as_posix()) > 200:
            warn("windows paths", f"{rel}: vault-relative path exceeds 200 characters")

    if any(part.casefold().startswith("onedrive") for part in vault.parts):
        warn("windows paths", f"vault is inside OneDrive: {vault}")
    attributes = read(vault / ".gitattributes")
    attribute_lines = {line.rstrip() for line in attributes.splitlines()
                       if not line.lstrip().startswith("#")}
    if not GIT_ATTRIBUTES.issubset(attribute_lines):
        warn("line endings", ".gitattributes is missing required eol=lf rules at vault root")

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
    configure_streams()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault", type=Path,
        default=Path(os.environ.get("BRAIN_HOME") or (Path.home() / "Brain")),
    )
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    issues = check(args.vault.expanduser().resolve(), args.today)
    for level, area, message in issues:
        print(SECRET.sub("[REDACTED]", f"{level} {area}: {message}"))
    print(f"vault-doctor: {len(issues)} issue(s)" if issues else "vault-doctor: OK")
    return int(any(level == "ERROR" for level, _, _ in issues))


if __name__ == "__main__":
    raise SystemExit(main())
