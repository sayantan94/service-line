"""A small reader for ASL-style workflow definitions.

Supports what Service Line workflows use: Pass, Task, Choice, Succeed and Fail
states, `$.a.b` paths, and the Choice rules StringEquals, NumericLessThan and And.
"""

from __future__ import annotations

import copy
from typing import Any

TERMINAL = ("Succeed", "Fail")


def _keys(path: str) -> list[str]:
    if path == "$":
        return []
    if not path.startswith("$."):
        raise ValueError(f"unsupported path: {path}")
    return path[2:].split(".")


def get_path(ctx: dict[str, Any], path: str) -> Any:
    value: Any = ctx
    for key in _keys(path):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def set_path(ctx: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Return a copy of `ctx` with `value` written at `path`."""
    keys = _keys(path)
    if not keys:
        return copy.deepcopy(value)
    out = copy.deepcopy(ctx)
    node = out
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = copy.deepcopy(value)
    return out


def matches(rule: dict[str, Any], ctx: dict[str, Any]) -> bool:
    if "And" in rule:
        return all(matches(r, ctx) for r in rule["And"])
    value = get_path(ctx, rule["Variable"])
    if "StringEquals" in rule:
        return value == rule["StringEquals"]
    if "NumericLessThan" in rule:
        return isinstance(value, (int, float)) and value < rule["NumericLessThan"]
    raise ValueError(f"unsupported choice rule: {sorted(rule)}")


def choose(state: dict[str, Any], ctx: dict[str, Any]) -> str:
    for rule in state["Choices"]:
        if matches(rule, ctx):
            return rule["Next"]
    return state["Default"]


def successors(state: dict[str, Any]) -> list[str]:
    if state["Type"] == "Choice":
        return [r["Next"] for r in state["Choices"]] + ([state["Default"]] if "Default" in state else [])
    return [state["Next"]] if "Next" in state else []
