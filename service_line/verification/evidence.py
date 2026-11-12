"""The evidence gate: decides whether a change may be called verified."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def evaluate(checks: dict[str, Any] | None, review: dict[str, Any] | None, head: str,
             plan_version: int | None, approval: dict[str, Any] | None) -> dict[str, Any]:
    """passed only when every check and the review passed on the current
    revision under the approved plan. failed when something was checked and
    found wrong. Anything missing, stale, or unreadable is inconclusive."""
    missing: list[str] = []
    failed: list[str] = []
    if not approval or approval.get("plan") != plan_version:
        missing.append("the current plan is not approved")
    results = (checks or {}).get("results") or []
    if not results:
        missing.append("no required check ran")
    if checks and checks.get("revision") != head:
        missing.append("check results belong to an older revision")
    for r in results:
        if r.get("timed_out") or r.get("exit_code") is None:
            missing.append(f"{r['id']} did not finish")
        elif r["exit_code"] != 0:
            failed.append(f"{r['id']} failed with exit {r['exit_code']}")
    if not review:
        missing.append("the verifier's review is missing")
    else:
        if review.get("revision") != head:
            missing.append("the review belongs to an older revision")
        if review.get("verdict") == "failed":
            failed.append("the verifier found a criterion not met")
        elif review.get("verdict") != "passed":
            missing.append("the verifier's review is inconclusive")
    verdict = "inconclusive" if missing else "failed" if failed else "passed"
    return {"verdict": verdict, "reasons": missing + failed, "revision": head}


def write_manifest(directory: Path, data: dict[str, Any]) -> None:
    """Record what was verified, with a hash of every artifact beside it."""
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(directory.iterdir()) if p.is_file() and p.name != "manifest.json"}
    (directory / "manifest.json").write_text(json.dumps({**data, "artifacts": hashes}, indent=2) + "\n")
