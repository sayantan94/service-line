"""A work item's checkout on this machine: a git worktree, and commands run
inside a sandbox that limits where they may write."""

from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

MODES = ("read-only", "workspace-write")
GRACE_SECONDS = 3


class SandboxUnavailable(Exception):
    """No way to confine commands here. The engine refuses to run them unconfined."""


@dataclass
class CommandResult:
    exit_code: int | None
    output: str
    timed_out: bool = False


def _real(path: Path | str) -> str:
    return os.path.realpath(str(path))


def confine(argv: list[str], mode: str, workspace: Path, extra_write: tuple[Path, ...] = (),
            platform: str = sys.platform) -> list[str]:
    """Wrap a command so that writes outside the allowed folders fail.

    read-only        nothing is writable except temporary folders
    workspace-write  the workspace and `extra_write` are writable too
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode}")
    roots = [_real("/tmp"), _real(tempfile.gettempdir())]
    roots += [_real(p) for p in extra_write]
    if mode == "workspace-write":
        roots.append(_real(workspace))
    roots = list(dict.fromkeys(roots))
    if platform == "darwin":
        quoted = " ".join('(subpath "%s")' % r.replace("\\", "\\\\").replace('"', '\\"') for r in roots)
        profile = f'(version 1) (allow default) (deny file-write*) (allow file-write* (literal "/dev/null")) (allow file-write* {quoted})'
        return ["/usr/bin/sandbox-exec", "-p", profile, "--", *argv]
    if platform.startswith("linux"):
        args = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--die-with-parent", "--tmpfs", "/tmp"]
        for root in roots:
            if root != "/tmp" and os.path.isdir(root):
                args += ["--bind", root, root]
        return [*args, "--", *argv]
    raise SandboxUnavailable(f"no sandbox for platform {platform!r}")


def stop_process_group(process: subprocess.Popen) -> None:
    """Signal the whole process group, wait briefly, then kill it."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=GRACE_SECONDS)
            return
        except subprocess.TimeoutExpired:
            continue


def run_command(argv: list[str], cwd: Path, timeout: float | None = None, stdin: str | None = None,
                env: dict[str, str] | None = None) -> CommandResult:
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               start_new_session=True, env=env)
    try:
        output, _ = process.communicate(stdin, timeout=timeout)
        return CommandResult(process.returncode, output)
    except subprocess.TimeoutExpired:
        stop_process_group(process)
        output, _ = process.communicate()
        return CommandResult(None, output or "", timed_out=True)


class Checkout:
    def __init__(self, repo: Path, path: Path):
        self.repo = Path(repo)
        self.path = Path(path)

    @classmethod
    def create(cls, repo: Path, path: Path, branch: str) -> "Checkout":
        checkout = cls(repo, path)
        if not (path / ".git").exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            exists = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
                                    cwd=repo, capture_output=True).returncode == 0
            args = ["worktree", "add", "-q", str(path), branch] if exists else ["worktree", "add", "-q", "-b", branch, str(path)]
            checkout._git(*args, cwd=repo)
        return checkout

    def _git(self, *args: str, cwd: Path | None = None) -> str:
        done = subprocess.run(["git", *args], cwd=cwd or self.path, capture_output=True, text=True)
        if done.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
        return done.stdout.strip()

    def head(self) -> str:
        return self._git("rev-parse", "HEAD")

    def status(self) -> str:
        return self._git("status", "--porcelain")

    def checkpoint(self, message: str) -> str:
        """Commit everything in the checkout. Returns the revision."""
        if self.status():
            self._git("add", "-A")
            self._git("-c", "user.name=Service Line", "-c", "user.email=service-line@localhost",
                      "commit", "-q", "--no-verify", "-m", message)
        return self.head()

    def reset(self, revision: str) -> None:
        """Return the checkout to a checkpoint, discarding everything since."""
        self._git("reset", "-q", "--hard", revision)
        self._git("clean", "-q", "-fd")

    def changed_files(self, since: str) -> list[str]:
        out = self._git("diff", "--name-only", since, "HEAD")
        return [line for line in out.splitlines() if line]

    def diff(self, since: str) -> str:
        return self._git("diff", since, "HEAD")

    def fingerprint(self) -> str:
        """A hash of the revision plus any uncommitted changes."""
        text = self.head() + "\n" + self.status() + "\n" + self._git("diff", "HEAD")
        for line in self.status().splitlines():
            if line.startswith("??"):
                target = self.path / line[3:]
                if target.is_file():
                    text += hashlib.sha256(target.read_bytes()).hexdigest()
        return hashlib.sha256(text.encode()).hexdigest()

    def run(self, argv: list[str], mode: str, timeout: float | None = None,
            extra_write: tuple[Path, ...] = ()) -> CommandResult:
        return run_command(confine(argv, mode, self.path, extra_write), self.path, timeout)
