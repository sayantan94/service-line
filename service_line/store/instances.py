"""Services: one folder per service under the Service Line home."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import atomic
from .workitems import WorkItem

EXECUTORS = ("Codex", "Claude")


class InstanceExists(Exception):
    """A service with this id is already registered."""


def other(executor: str) -> str:
    return "Claude" if executor == "Codex" else "Codex"


def default_home() -> Path:
    return Path(os.environ.get("SERVICE_LINE_HOME") or Path.cwd() / "instances")


def write_json(path: Path, data: dict) -> None:
    """Replace a small JSON file atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    with open(tmp, "rb") as handle:
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    atomic.fsync_dir(path.parent)


class Instance:
    def __init__(self, directory: Path):
        self.dir = directory
        data = json.loads((directory / "instance.json").read_text())
        self.id: str = directory.name
        self.name: str = data["name"]
        self.repo: str = data["repo"]
        self.implementer: str = data["implementer"]
        self.workflow: str = data.get("workflow", "software-change")
        self.guide: str = data.get("guide", "service-line-verification.md")

    def items(self) -> list[WorkItem]:
        root = self.dir / "workitems"
        if not root.exists():
            return []
        return [WorkItem(d, self) for d in sorted(root.iterdir()) if (d / "workitem.json").exists()]

    def item(self, item_id: str) -> WorkItem:
        return WorkItem(self.dir / "workitems" / item_id, self)

    def new_item(self, title: str, type: str, outcome: str, criteria: list[str],
                 implementer: str | None = None) -> WorkItem:
        number = len(self.items()) + 1
        directory = self.dir / "workitems" / f"WI-{number:03d}"
        write_json(directory / "workitem.json", {
            "title": title, "type": type, "outcome": outcome, "criteria": criteria,
            "implementer": implementer or self.implementer,
        })
        return WorkItem(directory, self)


class Home:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else default_home()

    def add(self, name: str, repo: str, implementer: str = "Codex", **extra: str) -> Instance:
        if implementer not in EXECUTORS:
            raise ValueError(f"implementer must be one of {EXECUTORS}")
        instance_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "service"
        directory = self.root / instance_id
        if (directory / "instance.json").exists():
            raise InstanceExists(instance_id)
        write_json(directory / "instance.json", {"name": name, "repo": repo, "implementer": implementer, **extra})
        return Instance(directory)

    def get(self, instance_id: str) -> Instance:
        return Instance(self.root / instance_id)

    def all(self) -> list[Instance]:
        if not self.root.exists():
            return []
        return [Instance(d) for d in sorted(self.root.iterdir()) if (d / "instance.json").exists()]
