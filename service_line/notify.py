"""Tells you when the line needs you."""

from __future__ import annotations

import subprocess
import sys

MESSAGES = {
    "waiting": "A plan is waiting for your approval",
    "ready": "Ready for your review",
    "needs_attention": "Needs your attention",
    "cancelled": "Cancelled",
    "failed": "The engine hit an error",
}


def notify(item_id: str, title: str, status: str, detail: str = "") -> str | None:
    text = MESSAGES.get(status)
    if text is None:
        return None
    line = f"{item_id} {title}: {text}" + (f" ({detail[:120]})" if detail else "")
    print(f"[service-line] {line}", flush=True)
    if sys.platform == "darwin":
        script = 'display notification "%s" with title "Service Line"' % line.replace("\\", "").replace('"', "'")
        subprocess.run(["osascript", "-e", script], capture_output=True)
    return line
