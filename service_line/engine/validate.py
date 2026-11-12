"""Checks a workflow definition before the engine will run it.

A workflow is refused when:
  - a state names a successor or action that does not exist;
  - implementation or repair can be reached without passing a human approval;
  - a loop has nothing that bounds it;
  - a state cannot reach an end.
"""

from __future__ import annotations

from typing import Any

from . import asl

APPROVAL = "service-line:approval.wait"
CHANGES_CODE = ("service-line:agent.implement", "service-line:repair.run")
KNOWN_ACTIONS = {
    "service-line:agent.research", "service-line:agent.plan", "service-line:agent.review-plan",
    APPROVAL, "service-line:agent.implement", "service-line:checks.run", "service-line:agent.verify",
    "service-line:verification.evaluate", "service-line:repair.run",
    "service-line:deployment.wait", "service-line:agent.observe", "service-line:observation.evaluate",
    "service-line:workitem.propose",
}
WAITS_FOR_SOMETHING_OUTSIDE = {APPROVAL, "service-line:deployment.wait"}


class WorkflowInvalid(Exception):
    pass


def _reachable(states: dict[str, Any], start: str, skip: set[str] = frozenset()) -> set[str]:
    seen: set[str] = set()
    stack = [start]
    while stack:
        name = stack.pop()
        if name in seen or name in skip:
            continue
        seen.add(name)
        stack.extend(asl.successors(states[name]))
    return seen


def _has_numeric_bound(rule: dict[str, Any]) -> bool:
    return "NumericLessThan" in rule or any(_has_numeric_bound(r) for r in rule.get("And", []))


def validate(definition: dict[str, Any]) -> None:
    states: dict[str, Any] = definition.get("States", {})
    start = definition.get("StartAt")
    if start not in states:
        raise WorkflowInvalid(f"StartAt names no state: {start!r}")

    for name, state in states.items():
        for target in asl.successors(state):
            if target not in states:
                raise WorkflowInvalid(f"{name} goes to a state that does not exist: {target}")
        if state["Type"] == "Task" and state.get("Resource") not in KNOWN_ACTIONS:
            raise WorkflowInvalid(f"{name} uses an action the engine does not have: {state.get('Resource')}")
        if state["Type"] not in asl.TERMINAL and not asl.successors(state):
            raise WorkflowInvalid(f"{name} has no next state and is not an end")

    approvals = {n for n, s in states.items() if s.get("Resource") == APPROVAL}
    without_approval = _reachable(states, start, skip=approvals)
    for name in without_approval:
        if states[name].get("Resource") in CHANGES_CODE:
            raise WorkflowInvalid(f"{name} can be reached without a human approval")

    ends = {n for n, s in states.items() if s["Type"] in asl.TERMINAL}
    for name in _reachable(states, start):
        if not (_reachable(states, name) & ends):
            raise WorkflowInvalid(f"{name} cannot reach an end; it is stuck in a loop")

    # Every loop must contain something that bounds it: a wait for something
    # outside the engine, or a Choice that only re-enters the loop under a
    # numeric limit.
    for name in _reachable(states, start):
        loop = {n for n in _reachable(states, name) if name in _reachable(states, n)}
        if name not in {t for n in loop for t in asl.successors(states[n])}:
            continue
        waits = any(states[n].get("Resource") in WAITS_FOR_SOMETHING_OUTSIDE for n in loop)
        bounded = False
        for n in loop:
            state = states[n]
            if state["Type"] != "Choice":
                continue
            into_loop = [r for r in state["Choices"] if r["Next"] in loop]
            default_in_loop = state.get("Default") in loop
            if into_loop and not default_in_loop and all(_has_numeric_bound(r) for r in into_loop):
                bounded = True
        if not (waits or bounded):
            raise WorkflowInvalid(f"the loop through {name} has no limit")
