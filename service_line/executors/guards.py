"""Guards against an agent that is stuck."""

from __future__ import annotations

import json
from typing import Any


class RepeatDetector:
    """Counts identical tool calls made one after another.

    Returns "remind" at each threshold before the last and "stop" at the last.
    A different call resets the count.
    """

    def __init__(self, thresholds: tuple[int, ...] = (3, 5, 8)):
        self.thresholds = thresholds
        self._key: str | None = None
        self._count = 0

    def observe(self, tool: str, arguments: Any) -> str | None:
        key = json.dumps([tool, arguments], sort_keys=True, default=str)
        self._count = self._count + 1 if key == self._key else 1
        self._key = key
        if self._count == self.thresholds[-1]:
            return "stop"
        return "remind" if self._count in self.thresholds else None
