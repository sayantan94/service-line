"""Durable file writes and the per-run lock."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def create_exclusive(path: Path, data: bytes) -> None:
    """Create `path` with `data`, durably, failing if it already exists.

    The data is written to a temporary file and synced, then linked into place.
    A link fails when the target exists, so a second creator cannot overwrite.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.link(tmp, path)
        fsync_dir(path.parent)
    finally:
        os.unlink(tmp)


def append_durable(path: Path, data: bytes) -> None:
    """Append `data` and sync. On failure, cut the file back to its old size."""
    fd = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        size = os.fstat(fd).st_size
        try:
            os.write(fd, data)
            os.fsync(fd)
        except BaseException:
            os.ftruncate(fd, size)
            os.fsync(fd)
            raise
    finally:
        os.close(fd)


def truncate_durable(path: Path, size: int) -> None:
    fd = os.open(path, os.O_WRONLY)
    try:
        os.ftruncate(fd, size)
        os.fsync(fd)
    finally:
        os.close(fd)


class LockHeld(Exception):
    """Another holder has the lock."""


class FileLock:
    """An exclusive, non-blocking lock. The kernel releases it if the process dies."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self._fd)
            self._fd = None
            raise LockHeld(str(path)) from None

    def release(self) -> None:
        if self._fd is not None:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = None
