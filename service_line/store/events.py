"""The run log: one append-only file of events per run.

The log is the only record of what happened in a run. Everything else, such as
the current step or the repair count, is computed by replaying it.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from . import atomic

FORMAT_VERSION = 1
LOG_NAME = "events.jsonl"
LOCK_NAME = "run.lock"


class LogExists(Exception):
    """A run log is already present where a new one was to be created."""


class RunLocked(Exception):
    """Another engine process has this run open."""


class LogCorrupt(Exception):
    """The log is damaged somewhere other than a torn final line."""


def _scan(raw: bytes) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    """Parse a log file. Returns the header, the events, and the number of
    bytes that hold complete records.

    A final line with no newline was cut off mid-write and is left out. Any
    other damage is an error: a bad line with good lines after it, or event
    numbers that do not count up from zero.
    """
    complete, _, _torn = raw.rpartition(b"\n")
    good_bytes = len(complete) + 1 if complete else 0
    records = []
    for number, line in enumerate(complete.split(b"\n") if complete else [], start=1):
        try:
            records.append(json.loads(line))
        except ValueError:
            raise LogCorrupt(f"line {number} is not valid JSON") from None
    if not records or records[0].get("type") != "run":
        raise LogCorrupt("missing run header")
    header, events = records[0], records[1:]
    for index, event in enumerate(events):
        if event.get("seq") != index:
            raise LogCorrupt(f"expected event {index}, found {event.get('seq')!r}")
    return header, events, good_bytes


def _line(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


class RunLog:
    def __init__(self, directory: Path, lock: atomic.FileLock, header: dict[str, Any],
                 events: list[dict[str, Any]], clock: Callable[[], int], good_bytes: int | None = None):
        self._path = directory / LOG_NAME
        self._good_bytes = good_bytes
        self._lock = lock
        self._header = header
        self._events = events
        self._clock = clock

    @classmethod
    def create(cls, directory: Path, run_id: str, clock: Callable[[], int] = _now_ms) -> "RunLog":
        directory = Path(directory)
        lock = cls._acquire(directory)
        header = {"type": "run", "version": FORMAT_VERSION, "id": run_id, "created": clock()}
        try:
            atomic.create_exclusive(directory / LOG_NAME, _line(header))
        except FileExistsError:
            lock.release()
            raise LogExists(str(directory / LOG_NAME)) from None
        except BaseException:
            lock.release()
            raise
        return cls(directory, lock, header, [], clock)

    @classmethod
    def open(cls, directory: Path, clock: Callable[[], int] = _now_ms) -> "RunLog":
        directory = Path(directory)
        lock = cls._acquire(directory)
        try:
            raw = (directory / LOG_NAME).read_bytes()
            header, events, good_bytes = _scan(raw)
        except BaseException:
            lock.release()
            raise
        torn = good_bytes if good_bytes < len(raw) else None
        return cls(directory, lock, header, events, clock, torn)

    @staticmethod
    def _acquire(directory: Path) -> atomic.FileLock:
        try:
            return atomic.FileLock(directory / LOCK_NAME)
        except atomic.LockHeld:
            raise RunLocked(str(directory)) from None

    @property
    def run_id(self) -> str:
        return self._header["id"]

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def append(self, type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Write one event and sync it to disk before returning."""
        event = {"seq": len(self._events), "time": self._clock(), "type": type, "data": data or {}}
        record = _line(event)
        if self._good_bytes is not None:
            # A torn final line is left alone on read and removed here, before
            # the first new write.
            atomic.truncate_durable(self._path, self._good_bytes)
            self._good_bytes = None
        atomic.append_durable(self._path, record)
        self._events.append(event)
        return event

    def close(self) -> None:
        self._lock.release()

    def __enter__(self) -> "RunLog":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
