#!/usr/bin/env python3
"""Produce a bounded, redacted chronological recovery brief from a transcript."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SECRET = re.compile(r"sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def redact(text: str) -> str:
    # Redact before truncating: a clipped credential must not escape detection.
    return SECRET.sub("[REDACTED]", text)


def clean_user(text: str) -> str:
    lines = [line for line in text.splitlines()
             if not line.lstrip().startswith("<command-")]
    text = "\n".join(lines)
    return re.sub(r"<system-reminder>.*?</system-reminder>", "", text,
                  flags=re.S).strip()


def digest(path: Path, budget: int) -> str:
    messages: list[str] = []
    timestamps: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    continue
                if record.get("timestamp"):
                    timestamps.append(str(record["timestamp"]))
                role = record.get("type")
                if role not in ("user", "assistant"):
                    continue
                content = record.get("message", {}).get("content", [])
                blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
                parts = []
                for block in blocks:
                    kind = block.get("type")
                    if kind == "text":
                        text = str(block.get("text", ""))
                        if role == "user":
                            # Entire system/command messages are client noise.
                            if text.lstrip().startswith(("<system-reminder>", "<command-")):
                                continue
                            text = clean_user(text)
                        if text.strip():
                            parts.append(f"{role.upper()}: {redact(text.strip())}")
                    elif kind == "tool_use" and role == "assistant":
                        args = block.get("input") or {}
                        detail = redact(str(args.get("file_path") or args.get("command") or args.get("description") or ""))
                        if not args.get("file_path"):
                            detail = detail[:80]
                        parts.append(f"TOOL: {redact(str(block.get('name', 'unknown')))} {detail}".replace("\n", " "))
                if parts:
                    messages.append("\n".join(parts)[:1500])
            except (ValueError, TypeError, AttributeError):
                continue
    header = f"Session: {redact(path.name)}"
    if timestamps:
        header += f" | {redact(timestamps[0])} — {redact(timestamps[-1])}"
    text = header + "\n" + "\n".join(messages)
    if len(text) > budget:
        first = budget // 4
        last = budget - first
        omitted = len(text) - budget
        text = text[:first] + f"\n[... {omitted} chars omitted ...]\n" + (text[-last:] if last else "")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--max-chars", type=int, default=24000)
    args = parser.parse_args()
    if args.max_chars < 1:
        parser.error("--max-chars must be positive")
    try:
        print(digest(args.transcript, args.max_chars))
    except OSError:
        parser.exit(1, "Unable to read transcript.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

