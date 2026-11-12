"""Drives Claude Code in headless mode.

The agent may never ask anyone: anything outside its allowed tools is denied.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import AgentResult, run_streaming
from .guards import RepeatDetector

TOOLS = {
    "read": "Read,Grep,Glob",
    "verify": "Read,Grep,Glob,Bash",
    "write": "Read,Grep,Glob,Bash,Edit,Write",
}


def command(access: str) -> list[str]:
    tools = TOOLS[access]
    return ["claude", "-p", "--output-format", "stream-json", "--verbose",
            "--permission-mode", "dontAsk", "--tools", tools, "--allowedTools", tools,
            "--no-session-persistence", "--disable-slash-commands", "--setting-sources", "project"]


def tool_calls(line: str) -> list[tuple[str, Any]]:
    try:
        event = json.loads(line)
        content = event["message"]["content"] if event.get("type") == "assistant" else []
        return [(b["name"], b.get("input")) for b in content if isinstance(b, dict) and b.get("type") == "tool_use"]
    except (ValueError, KeyError, TypeError):
        return []


def parse(lines: list[str], exit_code: int | None) -> AgentResult:
    """Complete only on exactly one successful result that has text."""
    results = []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "result":
            results.append(event)
    tail = "\n".join(lines[-5:])[-800:]
    if len(results) != 1:
        return AgentResult("", "error", f"expected one result, saw {len(results)} (exit {exit_code}): {tail}")
    result = results[0]
    text = result.get("result") or ""
    if result.get("subtype") != "success" or result.get("is_error") or not text.strip():
        return AgentResult(text, "error", f"result {result.get('subtype')!r} (exit {exit_code})")
    return AgentResult(text, "completed")


class Claude:
    name = "Claude"

    def run(self, prompt: str, cwd: Path, access: str, timeout: float) -> AgentResult:
        lines: list[str] = []
        repeats = RepeatDetector()

        def on_line(line: str) -> str | None:
            lines.append(line)
            for name, arguments in tool_calls(line):
                if repeats.observe(name, arguments) == "stop":
                    return "stuck"
            return None

        done = run_streaming(command(access), cwd, prompt, timeout, on_line)
        if done.stopped:
            return AgentResult("", done.stopped, f"stopped: {done.stopped}")
        return parse(lines, done.exit_code)
