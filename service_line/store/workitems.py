"""Work items: the request, its plans, your approvals, and its runs."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .instances import Instance


class NotApproved(Exception):
    """There is no plan to decide on, or the plan was not approved."""


def _versions(directory: Path, suffix: str) -> list[int]:
    if not directory.exists():
        return []
    return sorted(int(p.name[1:].split(".")[0]) for p in directory.glob(f"v*{suffix}"))


class WorkItem:
    def __init__(self, directory: Path, instance: "Instance"):
        self.dir = directory
        self.instance = instance
        self.id = directory.name
        data = json.loads((directory / "workitem.json").read_text())
        self.title: str = data["title"]
        self.type: str = data["type"]
        self.outcome: str = data["outcome"]
        self.criteria: list[str] = data["criteria"]
        self.implementer: str = data["implementer"]

    @property
    def verifier(self) -> str:
        from .instances import other
        return other(self.implementer)

    # plans
    def save_plan(self, text: str, risk: str, phases: list[str], review: str | None = None) -> int:
        from .instances import write_json
        version = (_versions(self.dir / "plans", ".json") or [0])[-1] + 1
        write_json(self.dir / "plans" / f"v{version}.json",
                   {"version": version, "risk": risk, "phases": phases, "text": text, "review": review})
        (self.dir / "plans" / f"v{version}.md").write_text(text + "\n")
        return version

    def plan(self) -> dict[str, Any] | None:
        versions = _versions(self.dir / "plans", ".json")
        if not versions:
            return None
        return json.loads((self.dir / "plans" / f"v{versions[-1]}.json").read_text())

    def set_review(self, review: str) -> None:
        from .instances import write_json
        plan = self.plan()
        plan["review"] = review
        write_json(self.dir / "plans" / f"v{plan['version']}.json", plan)

    def set_risk(self, risk: str) -> None:
        from .instances import write_json
        plan = self.plan()
        plan["risk"] = risk
        write_json(self.dir / "plans" / f"v{plan['version']}.json", plan)

    # approvals
    def decide(self, decision: str, feedback: str = "", guide_version: str | None = None) -> dict[str, Any]:
        """Record your decision on the current plan: approved, revise, or rejected."""
        from .instances import write_json
        plan = self.plan()
        if plan is None:
            raise NotApproved("there is no plan to decide on")
        record = {"decision": decision, "plan": plan["version"], "risk": plan["risk"],
                  "guide": guide_version, "feedback": feedback, "at": int(time.time())}
        write_json(self.dir / "approvals" / f"v{plan['version']}.json", record)
        return record

    def decision(self) -> dict[str, Any] | None:
        """Your decision on the current plan version, if you have made one."""
        plan = self.plan()
        if plan is None:
            return None
        path = self.dir / "approvals" / f"v{plan['version']}.json"
        return json.loads(path.read_text()) if path.exists() else None

    def approval(self) -> dict[str, Any] | None:
        decision = self.decision()
        return decision if decision and decision["decision"] == "approved" else None

    # runs
    def _run_numbers(self) -> list[int]:
        root = self.dir / "runs"
        return sorted(int(p.name[4:]) for p in root.glob("run-*")) if root.exists() else []

    def new_run_dir(self) -> Path:
        return self.dir / "runs" / f"run-{(self._run_numbers() or [0])[-1] + 1:03d}"

    def latest_run(self) -> Path | None:
        numbers = self._run_numbers()
        return self.dir / "runs" / f"run-{numbers[-1]:03d}" if numbers else None
