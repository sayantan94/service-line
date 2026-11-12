"""Drives Codex in non-interactive mode, inside Codex's own sandbox."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from .base import AgentResult, run_streaming
from .guards import RepeatDetector

SANDBOX = {"read": "read-only", "verify": "read-only", "write": "workspace-write"}


def command(access: str, cwd: Path, last_message: Path, prompt: str) -> list[str]:
    return ["codex", "exec", "--json", "--sandbox", SANDBOX[access], "-C", str(cwd),
            "--ephemeral", "--skip-git-repo-check", "-o", str(last_message), prompt]


def tool_calls(line: str) -> list[tuple[str, Any]]:
    try:
        item = json.loads(line).get("item") or {}
        if item.get("type") == "command_execution" and item.get("command"):
            return [("command", {"command": item["command"]})]
    except (ValueError, AttributeError):
        pass
    return []


def parse(exit_code: int | None, last_message: str, tail: str) -> AgentResult:
    if exit_code != 0:
        return AgentResult(last_message, "error", f"exit {exit_code}: {tail}")
    if not last_message.strip():
        return AgentResult("", "error", "finished without a final message")
    return AgentResult(last_message, "completed")


class Codex:
    name = "Codex"

    def run(self, prompt: str, cwd: Path, access: str, timeout: float) -> AgentResult:
        lines: list[str] = []
        repeats = RepeatDetector()
        started: set[str] = set()

        def on_line(line: str) -> str | None:
            lines.append(line)
            if '"item.started"' not in line and line not in started:
                return None
            for name, arguments in tool_calls(line):
                if repeats.observe(name, arguments) == "stop":
                    return "stuck"
            return None

        with tempfile.TemporaryDirectory() as scratch:
            last = Path(scratch) / "last-message.txt"
            done = run_streaming(command(access, cwd, last, prompt), cwd, None, timeout, on_line)
            message = last.read_text() if last.exists() else ""
        if done.stopped:
            return AgentResult(message, done.stopped, f"stopped: {done.stopped}")
        return parse(done.exit_code, message, "\n".join(lines[-5:])[-800:])
