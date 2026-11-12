"""What every step action shares: the run's environment and agent calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ... import skills
from ...executors.base import AgentResult, Executor
from ...policy import permissions
from ...store.events import RunLog
from ...store.workitems import WorkItem
from ...verification import guide as guides
from ...workspace.local import Checkout


class Waiting(Exception):
    """The run cannot continue until something outside the engine happens."""


class Halt(Exception):
    """The run stops for a human decision."""


ACCESS = {"Research": "read", "Plan": "read", "ReviewPlan": "read",
          "Implement": "write", "Repair": "write", "Review": "verify"}
SKILL_STEP = {"Research": "research", "Plan": "plan", "ReviewPlan": "review",
              "Implement": "implement", "Repair": "repair", "Review": "verify"}


@dataclass
class RunEnv:
    item: WorkItem
    checkout: Checkout
    log: RunLog
    run_dir: Path
    executors: dict[str, Executor]
    timeout: float = 900
    _calls: int = field(default=0, repr=False)

    def guide(self) -> guides.Guide:
        return guides.load(self.checkout.path / self.item.instance.guide)

    def executor_for(self, step: str) -> Executor:
        role = permissions.role_for(step)
        name = self.item.implementer if role == "implementer" else self.item.verifier
        return self.executors[name]

    def checkpoint(self, message: str) -> str:
        revision = self.checkout.checkpoint(message)
        self.log.append("checkpoint", {"revision": revision, "message": message})
        return revision

    def save(self, name: str, text: str) -> str:
        path = self.run_dir / "artifacts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return str(path.relative_to(self.run_dir))

    def agent(self, step: str, task: str) -> AgentResult:
        """Run one agent call for a step, inside that step's limits.

        The call is logged as started before it runs and as ended after. A
        stuck, timed-out, or failed agent stops the run for a decision.
        """
        executor = self.executor_for(step)
        instructions = skills.load(SKILL_STEP[step], Path(self.item.instance.repo))
        prompt = (f"You are the {permissions.role_for(step)} for one step of a fixed workflow: {step}.\n"
                  f"Nobody can answer questions during this step. Do the step and stop.\n\n"
                  f"## How to do this step\n{instructions}\n\n## The task\n{task}\n")
        self._calls += 1
        self.save(f"{self._calls:02d}-{step}-prompt.md", prompt)
        call = self.log.start("call", step=step, executor=executor.name, access=ACCESS[step])
        try:
            result = executor.run(prompt, self.checkout.path, ACCESS[step], self.timeout)
        except BaseException:
            raise                       # left open on purpose: the outcome is unknown
        self.log.end("call", call, result.stop_reason, diagnostic=result.diagnostic[:500])
        self.save(f"{self._calls:02d}-{step}-output.md", result.output)
        if not result.ok:
            raise Halt(f"{executor.name} did not finish {step}: {result.stop_reason}. {result.diagnostic[:300]}")
        return result


def describe(item: WorkItem) -> str:
    criteria = "\n".join(f"AC{i + 1}. {c}" for i, c in enumerate(item.criteria))
    return f"Work item {item.id}: {item.title} ({item.type})\n\nOutcome wanted:\n{item.outcome}\n\nAcceptance criteria:\n{criteria}"
