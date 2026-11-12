"""Runs work items in the background, a limited number at a time."""

from __future__ import annotations

import threading
import traceback
from typing import Callable

from .engine import line
from .notify import notify
from .store.workitems import WorkItem


class Queue:
    def __init__(self, executors=None, home=None, max_running: int = 1,
                 advance: Callable[..., str] = line.advance, on_done: Callable[..., object] = notify):
        self.executors, self.home = executors, home
        self._advance, self._on_done = advance, on_done
        self._slots = threading.Semaphore(max_running)
        self._lock = threading.Lock()
        self._active: dict[str, threading.Thread] = {}
        self._last: dict[str, threading.Thread] = {}
        self.errors: dict[str, str] = {}

    @staticmethod
    def key(item: WorkItem) -> str:
        return f"{item.instance.id}/{item.id}"

    def busy(self, item: WorkItem) -> bool:
        with self._lock:
            thread = self._active.get(self.key(item))
            return bool(thread and thread.is_alive())

    def submit(self, item: WorkItem) -> bool:
        """Start or continue a work item. Returns False if it is already running."""
        key = self.key(item)
        with self._lock:
            thread = self._active.get(key)
            if thread and thread.is_alive():
                return False
            self.errors.pop(key, None)
            thread = threading.Thread(target=self._work, args=(item, key), daemon=True, name=f"line-{key}")
            self._active[key] = self._last[key] = thread
            thread.start()
            return True

    def _work(self, item: WorkItem, key: str) -> None:
        with self._slots:
            try:
                status = self._advance(item, self.executors, home=self.home)
                detail = line.status(item).get("detail", "")
            except Exception as error:                   # an engine fault, not an agent failure
                status, detail = "failed", f"{type(error).__name__}: {error}"
                self.errors[key] = detail + "\n" + traceback.format_exc()
        # The item is free for its next step before anyone is told about it:
        # a slow notification must not hold up a decision.
        with self._lock:
            if self._active.get(key) is threading.current_thread():
                del self._active[key]
        self._on_done(item.id, item.title, status, detail)

    def wait(self, item: WorkItem, timeout: float | None = None) -> None:
        with self._lock:
            thread = self._last.get(self.key(item))
        if thread:
            thread.join(timeout)
