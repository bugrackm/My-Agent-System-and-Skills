#!/usr/bin/env python3
"""Copy the Windows brain hook and agent from the vault runtime into Claude Code."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

FILES = ("hooks/brain-memory.py", "agents/memory-keeper.md")


def same_file(source: Path, target: Path) -> bool:
    try:
        return source.read_bytes().replace(b"\r\n", b"\n") == target.read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return False


def backup_path(target: Path) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    candidate = target.with_name(f"{target.name}.backup-{stamp}")
    index = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.name}.backup-{stamp}-{index}")
        index += 1
    return candidate


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--brain-home", type=Path,
        default=Path(os.environ.get("BRAIN_HOME") or (Path.home() / "Brain")),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    brain_home = args.brain_home.expanduser().resolve()
    claude_home = (Path.home() / ".claude").resolve()
    missing = [brain_home / "runtime" / name for name in FILES
               if not (brain_home / "runtime" / name).is_file()]
    if missing:
        for path in missing:
            print(f"error: source is missing: {path}", file=sys.stderr)
        return 1

    actions: list[tuple[Path, Path, Path | None]] = []
    for name in FILES:
        source = brain_home / "runtime" / name
        target = claude_home / name
        if same_file(source, target):
            print(f"up to date: {target}")
            continue
        backup = backup_path(target) if target.exists() else None
        actions.append((source, target, backup))
        if backup:
            print(f"backup: {target} -> {backup}")
        print(f"copy: {source} -> {target}")

    if not actions:
        print("runtime already up to date")
        return 0
    if args.dry_run:
        print("(dry run: nothing written)")
        return 0
    for source, target, backup in actions:
        target.parent.mkdir(parents=True, exist_ok=True)
        if backup:
            shutil.copy2(target, backup)
        shutil.copy2(source, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
