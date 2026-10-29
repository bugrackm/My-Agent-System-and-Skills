#!/usr/bin/env python3
"""Merge the brain hooks into ~/.claude/settings.json without touching anything else.

- Backs up the existing settings.json first (settings.json.backup-<timestamp>).
- Adds each hook command from runtime/settings.template.json only if that exact
  command is not already registered for the event, so re-running is safe.
- Sets env.BRAIN_HOME (so hooks and memory-keeper find the vault) unless it is
  already set; an existing value is never overwritten.

Usage: python3 brain/merge-settings.py [--brain-home PATH] [--settings PATH] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "runtime" / "settings.template.json"


def validate(settings: dict, template: dict) -> str | None:
    """Return an error message if settings has a shape merge() cannot extend safely."""
    for key in ("hooks", "env"):
        if key in settings and not isinstance(settings[key], dict):
            return f'"{key}" exists but is not an object'
    for event in template.get("hooks", {}):
        live = settings.get("hooks", {}).get(event)
        if live is not None and not isinstance(live, list):
            return f'"hooks.{event}" exists but is not a list'
    return None


def merge(settings: dict, template: dict, brain_home: str) -> list[str]:
    changes = []
    hooks = settings.setdefault("hooks", {})
    for event, groups in template.get("hooks", {}).items():
        live = hooks.setdefault(event, [])
        installed = {h.get("command") for g in live for h in g.get("hooks", [])}
        for group in groups:
            new = [h for h in group.get("hooks", []) if h.get("command") not in installed]
            if new:
                live.append({**group, "hooks": new})
                changes.append(f"hooks.{event}: added {len(new)} command(s)")
    env = settings.setdefault("env", {})
    if "BRAIN_HOME" not in env:
        env["BRAIN_HOME"] = brain_home
        changes.append(f"env.BRAIN_HOME = {brain_home}")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brain-home", default=str(Path.home() / "Documents" / "Brain"))
    parser.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    try:
        settings = json.loads(args.settings.read_text(encoding="utf-8")) if args.settings.exists() else {}
    except (ValueError, OSError) as exc:
        print(f"error: {args.settings} is not valid JSON ({exc}); fix it first", file=sys.stderr)
        return 1

    problem = validate(settings, template)
    if problem:
        print(f"error: {args.settings}: {problem}; fix it first (nothing written)", file=sys.stderr)
        return 1

    changes = merge(settings, template, str(Path(args.brain_home).expanduser()))
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
        shutil.copy2(args.settings, backup)
        print(f"backup: {backup}")
    args.settings.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.settings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
