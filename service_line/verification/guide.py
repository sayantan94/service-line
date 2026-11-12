"""Reads a service's verification guide: the commands that must pass."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Check:
    id: str
    command: str


@dataclass
class Guide:
    version: str | None
    text: str = ""
    checks: list[Check] = field(default_factory=list)
    high_paths: list[str] = field(default_factory=list)


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M | re.I)
    return match.group(1) if match else ""


def load(path: Path) -> Guide:
    if not path.exists():
        return Guide(version=None)
    text = path.read_text()
    checks = []
    for row in _section(text, "Required commands").splitlines():
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0].lower() == "id":
            continue
        command = cells[1].strip("`").strip()
        if command and "<" not in command:      # skip unfilled template rows
            checks.append(Check(cells[0], command))
    high = re.search(r"^High-risk paths:\s*(.+)$", text, re.M | re.I)
    paths = [p.strip(" `") for p in high.group(1).split(",")] if high else []
    return Guide(hashlib.sha256(text.encode()).hexdigest()[:12], text, checks, [p for p in paths if p])
