"""What every executor returns, and how the engine runs and stops one."""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from ..workspace.local import stop_process_group

ACCESS = ("read", "verify", "write")   # read files; also run commands; also edit
STOP_REASONS = ("completed", "error", "timeout", "stuck")


@dataclass
class AgentResult:
    """A run always ends in one of these. A failed agent is a result, not an exception."""
    output: str
    stop_reason: str
    diagnostic: str = ""

    @property
    def ok(self) -> bool:
        return self.stop_reason == "completed"


class Executor(Protocol):
    name: str

    def run(self, prompt: str, cwd: Path, access: str, timeout: float) -> AgentResult: ...


@dataclass
class Finished:
    exit_code: int | None
    stopped: str | None      # None, "timeout", or the reason a line handler gave


def run_streaming(argv: list[str], cwd: Path, stdin: str | None, timeout: float,
                  on_line: Callable[[str], str | None], env: dict[str, str] | None = None) -> Finished:
    """Run a command, handing each output line to `on_line`.

    The run is stopped when the time limit passes or when `on_line` returns a
    reason. Stopping always signals the whole process group, then kills it.
    """
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               start_new_session=True, env=env)
    stopped: list[str] = []
    stop_once = threading.Lock()

    def stop(reason: str) -> None:
        with stop_once:
            if stopped:
                return
            stopped.append(reason)
        stop_process_group(process)

    timer = threading.Timer(timeout, stop, args=("timeout",))
    timer.daemon = True
    timer.start()
    try:
        if stdin is not None:
            try:
                process.stdin.write(stdin)
                process.stdin.close()
            except BrokenPipeError:
                pass
        for raw in process.stdout:
            reason = on_line(raw.rstrip("\n"))
            if reason:
                stop(reason)
                break
        process.wait()
    finally:
        timer.cancel()
    return Finished(process.returncode if not stopped else None, stopped[0] if stopped else None)
