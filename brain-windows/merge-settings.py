#!/usr/bin/env python3
"""Merge Windows brain hooks into Claude Code settings without clobbering other settings.

Usage: python brain-windows/merge-settings.py [--python PATH] [--hook PATH]
       [--brain-home PATH] [--settings PATH] [--update] [--dry-run]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

EVENTS = {
    "SessionStart": ("session-start", 30),
    "UserPromptSubmit": ("prompt", 15),
    "Stop": ("stop", 15),
    "SessionEnd": ("session-end", 15),
}


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass


def absolute_forward(path: str | Path) -> str:
    return Path(path).expanduser().resolve().as_posix()


def ps_quote(path: str) -> str:
    for quote in ("'", "\u2018", "\u2019", "\u201a", "\u201b"):
        path = path.replace(quote, quote * 2)
    return "'" + path + "'"


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


def hook_identity(command: object, argument: str) -> bool:
    decoded = decode_hook_command(command)
    if "brain-memory.py" not in decoded:
        return False
    encoded = isinstance(command, str) and decoded != command
    if encoded:
        return re.search(
            rf"\s{re.escape(argument)};\s*exit\s+\$LASTEXITCODE\s*$",
            decoded,
            flags=re.IGNORECASE,
        ) is not None
    return re.search(
        rf"(?:^|\s){re.escape(argument)}\s*$", decoded, flags=re.IGNORECASE
    ) is not None


def is_brain_hook(command: object) -> bool:
    return "brain-memory.py" in decode_hook_command(command)


def render_hook(python: str, hook: str, argument: str, timeout: int) -> dict:
    system_root = os.environ.get("SystemRoot", "C:/Windows").replace("\\", "/").rstrip("/")
    powershell = system_root + "/System32/WindowsPowerShell/v1.0/powershell.exe"
    assert " " not in powershell, f"PowerShell path contains a space: {powershell}"
    script = f"& {ps_quote(python)} {ps_quote(hook)} {argument}; exit $LASTEXITCODE"
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    command = (
        f"{powershell} -NoProfile -NonInteractive -ExecutionPolicy Bypass "
        f"-EncodedCommand {encoded}"
    )
    return {"type": "command", "command": command, "timeout": timeout}


def invalid_command_path(path: str) -> bool:
    return any(char in path for char in ("\n", "\r", "\0"))


def validate(settings: dict) -> str | None:
    for key in ("hooks", "env"):
        if key in settings and not isinstance(settings[key], dict):
            return f'"{key}" exists but is not an object'
    for event in EVENTS:
        live = settings.get("hooks", {}).get(event)
        if live is not None and not isinstance(live, list):
            return f'"hooks.{event}" exists but is not a list'
        if isinstance(live, list):
            for group in live:
                if not isinstance(group, dict):
                    return f'"hooks.{event}" contains an invalid hook group'
                if not isinstance(group.get("hooks", []), list):
                    return f'"hooks.{event}" contains a hook group whose "hooks" is not a list'
                if any(not isinstance(item, dict) for item in group.get("hooks", [])):
                    return f'"hooks.{event}" contains a non-object hook entry'
    return None


def merge(settings: dict, python: str, hook: str, brain_home: str, update: bool) -> list[str]:
    changes: list[str] = []
    hooks = settings.setdefault("hooks", {})
    for event, (argument, timeout) in EVENTS.items():
        live = hooks.setdefault(event, [])
        rendered = render_hook(python, hook, argument, timeout)
        found = False
        if update:
            for group in live:
                for index, item in enumerate(group.get("hooks", [])):
                    if is_brain_hook(item.get("command")):
                        found = True
                        if item != rendered:
                            group["hooks"][index] = rendered
                            changes.append(f"hooks.{event}: updated brain-memory.py command")
            if not found:
                live.append({"hooks": [rendered]})
                changes.append(f"hooks.{event}: added brain-memory.py command")
        else:
            found = any(
                hook_identity(item.get("command"), argument)
                for group in live for item in group.get("hooks", [])
            )
            if not found:
                live.append({"hooks": [rendered]})
                changes.append(f"hooks.{event}: added brain-memory.py command")
    env = settings.setdefault("env", {})
    for key, value in (("BRAIN_HOME", brain_home), ("BRAIN_PYTHON", python)):
        if key not in env or (update and env[key] != value):
            env[key] = value
            changes.append(f"env.{key} = {value}")
    return changes


def warn_environment(python: str, brain_home: str) -> None:
    for label, value in (("Python path", python), ("brain home", brain_home)):
        if any(part.startswith("onedrive")
               for part in value.casefold().replace("\\", "/").split("/")):
            print(f"warning: {label} is inside OneDrive: {value}", file=sys.stderr)
    if "windowsapps" in python.casefold().replace("\\", "/").split("/"):
        print(
            "warning: Python is under WindowsApps and may be a Microsoft Store alias; "
            "install Python from python.org and pass its executable with --python",
            file=sys.stderr,
        )
    if shutil.which("git") is None:
        print("warning: git was not found on PATH; vault synchronization will be unavailable", file=sys.stderr)


def main() -> int:
    configure_streams()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--hook", default=str(Path.home() / ".claude" / "hooks" / "brain-memory.py"))
    parser.add_argument("--brain-home", default=str(Path.home() / "Brain"))
    parser.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for label, value in (("Python", args.python), ("hook", args.hook)):
        if invalid_command_path(value):
            print(f"error: {label} path contains a newline, carriage return, or NUL (nothing written)",
                  file=sys.stderr)
            return 2
    python = absolute_forward(args.python)
    hook = absolute_forward(args.hook)
    brain_home = absolute_forward(args.brain_home)
    warn_environment(python, brain_home)
    try:
        settings = json.loads(args.settings.read_text(encoding="utf-8-sig")) if args.settings.exists() else {}
    except (ValueError, OSError) as exc:
        print(f"error: {args.settings} is not valid JSON ({exc}); fix it first", file=sys.stderr)
        return 1
    if not isinstance(settings, dict):
        print(f"error: {args.settings}: top level is not an object; fix it first", file=sys.stderr)
        return 1
    problem = validate(settings)
    if problem:
        print(f"error: {args.settings}: {problem}; fix it first (nothing written)", file=sys.stderr)
        return 2

    changes = merge(settings, python, hook, brain_home, args.update)
    if not changes:
        print("settings.json already up to date")
        return 0
    for change in changes:
        print(change)
    if args.dry_run:
        print("(dry run: nothing written)")
        return 0

    args.settings.parent.mkdir(parents=True, exist_ok=True)
    if args.settings.exists():
        backup = args.settings.with_name(f"settings.json.backup-{time.strftime('%Y%m%d-%H%M%S')}")
        suffix = 1
        while backup.exists():
            backup = args.settings.with_name(
                f"settings.json.backup-{time.strftime('%Y%m%d-%H%M%S')}-{suffix}"
            )
            suffix += 1
        shutil.copy2(args.settings, backup)
        print(f"backup: {backup}")
    output = json.dumps(settings, indent=2, ensure_ascii=True) + "\n"
    fd, temporary_name = tempfile.mkstemp(
        dir=args.settings.parent, prefix=f".{args.settings.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as temporary:
            temporary.write(output)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, args.settings)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
    print(f"wrote {args.settings}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
