"""Steps a run through its workflow, one state at a time.

Everything the runner knows comes from the run log. Each state is bracketed by
a start and an end event; the end event carries what the state produced and
which state comes next. After a crash the runner closes what was open and runs
that state again, from the last checkpoint when it cannot tell what happened.
"""

from __future__ import annotations

from typing import Any, Callable

from ..policy import killswitch
from ..store.events import RunLog, close_open
from . import asl
from .actions import REGISTRY, Halt, RunEnv, Waiting

FAIL_STATUS = {"VerificationNeedsAttention": "needs_attention", "PlanNotApproved": "cancelled"}


def replay(definition: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute where a run stands from its events alone."""
    state = {"current": definition["StartAt"], "ctx": {}, "status": "running", "detail": "", "revision": None}
    for event in events:
        kind, data = event["type"], event["data"]
        if kind == "state/end":
            if data["reason"] == "completed":
                if "set" in data:
                    state["ctx"] = asl.set_path(state["ctx"], data["set"]["path"], data["set"]["value"])
                state["current"] = data.get("next") or state["current"]
                state["status"] = "running"
            elif data["reason"] == "waiting":
                state["status"], state["detail"] = "waiting", data.get("detail", "")
        elif kind == "state/start":
            if state["status"] == "waiting":
                state["status"] = "running"
        elif kind == "checkpoint":
            state["revision"] = data["revision"]
        elif kind == "run/end":
            state["status"], state["detail"] = data["status"], data.get("cause", "")
    return state


class Runner:
    def __init__(self, definition: dict[str, Any], env: RunEnv,
                 actions: dict[str, Callable[..., dict]] = REGISTRY, home=None):
        self.definition = definition
        self.states = definition["States"]
        self.env = env
        self.log: RunLog = env.log
        self.actions = actions
        self.home = home

    def recover(self) -> None:
        """Close whatever a crash left open. Reset the checkout if a side effect
        may have run, so the state never re-runs on half-finished changes."""
        found = close_open(self.log)
        if found["outcome"] in ("unknown", "effects-finished"):
            revision = replay(self.definition, self.log.events)["revision"] or self.env.checkout.head()
            self.env.checkout.reset(revision)
            self.log.append("recovery", {"state": found["state"], "outcome": found["outcome"], "reset_to": revision})

    def run(self) -> str:
        """Run until the workflow ends, waits for a person, or is stopped."""
        self.recover()
        while True:
            where = replay(self.definition, self.log.events)
            if where["status"] not in ("running", "waiting"):
                return where["status"]
            if self.home is not None and killswitch.engaged(self.home):
                return "stopped"
            name, ctx = where["current"], where["ctx"]
            state = self.states[name]
            started = self.log.start("state", name=name)
            kind = state["Type"]
            if kind == "Succeed":
                self.log.end("state", started, "completed")
                self.log.append("run/end", {"status": "ready"})
            elif kind == "Fail":
                self.log.end("state", started, "completed")
                self.log.append("run/end", {"status": FAIL_STATUS.get(state.get("Error"), "failed"),
                                            "error": state.get("Error"), "cause": state.get("Cause", "")})
            elif kind == "Choice":
                self.log.end("state", started, "completed", next=asl.choose(state, ctx))
            elif kind == "Pass":
                self._finish(started, state, state.get("Result"))
            else:
                self.env.timeout = state.get("TimeoutSeconds", 900)
                try:
                    result = self.actions[state["Resource"]](self.env, ctx, state)
                except Waiting as wait:
                    self.log.end("state", started, "waiting", detail=str(wait))
                    return "waiting"
                except Halt as halt:
                    self.log.end("state", started, "halted", detail=str(halt))
                    self.log.append("run/end", {"status": "needs_attention", "cause": str(halt)})
                    return "needs_attention"
                except Exception as error:
                    self.log.end("state", started, "failed", detail=f"{type(error).__name__}: {error}")
                    raise
                self._finish(started, state, result)

    def _finish(self, started: int, state: dict[str, Any], result: Any) -> None:
        extra = {"set": {"path": state["ResultPath"], "value": result}} if "ResultPath" in state else {}
        self.log.end("state", started, "completed", next=state["Next"], **extra)
