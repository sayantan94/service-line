"""Starting and continuing a work item's run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..executors.base import Executor
from ..store.events import LOG_NAME, RunLog
from ..store.workitems import WorkItem
from ..workspace.local import Checkout
from .actions import RunEnv
from .runner import Runner, replay
from .validate import validate

WORKFLOWS = Path(__file__).parent.parent.parent / "workflows"


def definition_for(item: WorkItem) -> dict[str, Any]:
    definition = json.loads((WORKFLOWS / f"{item.instance.workflow}.asl.json").read_text())
    validate(definition)
    return definition


def default_executors() -> dict[str, Executor]:
    from ..executors.claude import Claude
    from ..executors.codex import Codex
    return {"Claude": Claude(), "Codex": Codex()}


def advance(item: WorkItem, executors: dict[str, Executor] | None = None, home: Path | None = None) -> str:
    """Start the work item's run, or continue it. Returns the run's status."""
    definition = definition_for(item)
    run_dir = item.latest_run()
    new = run_dir is None or not (run_dir / LOG_NAME).exists()
    if new:
        run_dir = item.new_run_dir()
    checkout = Checkout.create(Path(item.instance.repo), item.dir / "workspace", branch=f"service-line/{item.instance.id}-{item.id}")
    log = RunLog.create(run_dir, run_id=run_dir.name) if new else RunLog.open(run_dir)
    try:
        if new:
            log.append("run/start", {"workflow": item.instance.workflow, "workItem": item.id,
                                     "implementer": item.implementer, "verifier": item.verifier,
                                     "base": checkout.head()})
        env = RunEnv(item, checkout, log, run_dir, executors or default_executors())
        return Runner(definition, env, home=home).run()
    finally:
        log.close()


def status(item: WorkItem) -> dict[str, Any]:
    """Where a work item stands, read from its run log without locking it."""
    run_dir = item.latest_run()
    if run_dir is None or not (run_dir / LOG_NAME).exists():
        return {"status": "queued", "current": None, "ctx": {}, "detail": "", "events": []}
    from ..store.events import _scan
    _, events, _ = _scan((run_dir / LOG_NAME).read_bytes())
    return {**replay(definition_for(item), events), "events": events, "run": run_dir.name}
