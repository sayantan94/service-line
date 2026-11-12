"""The local web server: serves the UI and the data behind it."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from . import skills
from .engine import line
from .policy import killswitch
from .queue import Queue
from .store.instances import EXECUTORS, Home, Instance
from .store.workitems import WorkItem
from .verification import guide as guides

ROOT = Path(__file__).parent.parent
UI = ROOT / "service-line-ui-next.html"
PLANNING = ("Initialize", "Research", "Plan", "ReviewPlan")
NOTE = {"run/start": "Run started", "checkpoint": "Checkpoint saved", "recovery": "Recovered after an interruption",
        "run/end": "Run ended"}


def _note(event: dict[str, Any]) -> str:
    kind, d = event["type"], event["data"]
    if kind == "state/start":
        return d.get("name", "")
    if kind == "state/end":
        return " ".join(str(x) for x in (d.get("reason"), "then " + d["next"] if d.get("next") else "", d.get("detail", "")) if x)
    if kind == "call/start":
        return f"{d.get('executor')} starts {d.get('step')}"
    if kind == "call/end":
        return f"{d.get('reason')} {d.get('diagnostic', '')}".strip()
    if kind == "check/start":
        return f"{d.get('id')}: {d.get('command')}"
    if kind == "check/end":
        return f"exit {d.get('exit_code')}" if d.get("reason") == "completed" else "timed out"
    if kind == "run/end":
        return f"{d.get('status')} {d.get('cause', '')}".strip()
    if kind == "checkpoint":
        return f"{d.get('revision', '')[:8]} {d.get('message', '')}"
    return NOTE.get(kind, json.dumps(d)[:120])


class App:
    def __init__(self, home: Home, queue: Queue | None = None):
        self.home = home
        self.queue = queue or Queue(home=home.root)

    # ---- reading
    def item_view(self, item: WorkItem) -> dict[str, Any]:
        where = line.status(item)
        ctx, plan, decision = where["ctx"], item.plan(), item.decision()
        status, current, busy = where["status"], where.get("current"), self.queue.busy(item)
        phase = "queued"
        if status == "queued":
            ui = "queued"
        elif status in ("running", "waiting", "stopped"):
            if status == "waiting" and decision is None:
                ui, phase = "waiting", "approval"
            elif current in PLANNING or current in ("AwaitApproval", "ApprovalDecision") and not item.approval():
                ui, phase = "planning", "plan"
            else:
                ui = "running"
                phase = "implement" if current == "Implement" else "repair" if current == "Repair" else "review"
        elif status == "ready":
            ui, phase = "ready", "done"
        elif status == "cancelled":
            ui, phase = "cancelled", "cancelled"
        else:
            ui, phase = "blocked", "limit"
        results: dict[str, Any] = {}
        run_dir = item.latest_run()
        for r in ctx.get("checks", {}).get("results", []):
            verdict = "inconclusive" if r["timed_out"] or r["exit_code"] is None else "passed" if r["exit_code"] == 0 else "failed"
            out = (run_dir / r["output"]).read_text()[-4000:] if run_dir and (run_dir / r["output"]).exists() else ""
            results[r["id"]] = {"status": verdict, "out": out}
        review = ctx.get("review")
        if review:
            path = run_dir / review["findings"] if run_dir else None
            results["review"] = {"status": review["verdict"], "out": path.read_text()[-4000:] if path and path.exists() else ""}
        checks = guides.load(Path(item.instance.repo) / item.instance.guide).checks
        phases = [[p.split(":", 1)[0].strip(), p.split(":", 1)[1].strip() if ":" in p else ""] for p in (plan or {}).get("phases", [])]
        return {
            "id": item.id, "title": item.title, "type": item.type, "executor": item.implementer,
            "risk": (plan or {}).get("risk", "low"), "status": ui, "phase": phase, "desc": item.outcome,
            "phases": phases, "criteria": item.criteria, "checks": [c.id for c in checks], "results": results,
            "repairs": ctx.get("repairs", 0), "attempt": ctx.get("checks", {}).get("attempt", 0),
            "revision": (ctx.get("implementation", {}).get("revision") or "")[:8] or "none yet",
            "version": (plan or {}).get("version", 1), "approved": plan["version"] if item.approval() else None,
            "feedback": (decision or {}).get("feedback", ""), "review": (plan or {}).get("review") or "",
            "planText": (plan or {}).get("text", ""), "busy": busy, "detail": where.get("detail", ""),
            "current": current, "gate": ctx.get("verification"),
            "error": self.queue.errors.get(self.queue.key(item), ""),
            "log": [[e["type"], _note(e)] for e in where["events"]],
        }

    def state(self) -> dict[str, Any]:
        services = {}
        for inst in self.home.all():
            checks = guides.load(Path(inst.repo) / inst.guide).checks
            services[inst.id] = {"name": inst.name, "repo": inst.repo, "implementer": inst.implementer,
                                 "checks": {c.id: [c.id, c.command] for c in checks},
                                 "items": [self.item_view(w) for w in reversed(inst.items())]}
        return {"live": True, "stopped": killswitch.engaged(self.home.root), "services": services}

    def files(self, service: str, item_id: str | None) -> list[dict[str, str]]:
        inst = self.home.get(service)
        out: list[dict[str, str]] = []

        def add(path: Path, shown: str, about: str) -> None:
            if path.is_file():
                out.append({"path": shown, "about": about, "text": path.read_text(errors="replace")[:60000]})

        add(line.WORKFLOWS / f"{inst.workflow}.asl.json", f"workflows/{inst.workflow}.asl.json", "The workflow definition. A run pins one version of it.")
        for step in sorted(p.name for p in skills.ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")):
            for name in skills.names(step):
                add(skills.ROOT / step / name / "SKILL.md", f"skills/{step}/{name}/SKILL.md", "An instruction file the engine hands an agent for this step.")
        add(Path(inst.repo) / inst.guide, f"{inst.repo}/{inst.guide}", "The service's own guide: what to run and what evidence is required.")
        add(inst.dir / "instance.json", f"instances/{inst.id}/instance.json", "The service: its repository and defaults.")
        if item_id:
            base = inst.item(item_id).dir
            skip = base / "workspace"
            for path in sorted(p for p in base.rglob("*") if p.is_file() and skip not in p.parents and p.name != "run.lock"):
                rel = path.relative_to(inst.dir)
                about = ("The run log. One event per line; everything else is computed from it." if path.name == "events.jsonl"
                         else "Your decision. It binds the plan, the risk level and the checks." if "approvals" in rel.parts
                         else "The plan the implementer wrote." if "plans" in rel.parts
                         else "What you asked for." if path.name == "workitem.json"
                         else "Recorded by the engine during the run.")
                add(path, f"instances/{inst.id}/{rel}", about)
        return out

    # ---- acting
    def add_service(self, name: str, repo: str, implementer: str = "Codex") -> str:
        repo_path = Path(repo).expanduser().resolve()
        if not (repo_path / ".git").exists():
            raise ValueError(f"{repo_path} is not a git repository")
        return self.home.add(name, repo=str(repo_path), implementer=implementer).id

    def new_item(self, service: str, title: str, type: str, outcome: str, criteria: list[str], implementer: str | None = None) -> str:
        if not title.strip() or not outcome.strip() or not criteria:
            raise ValueError("a work item needs a title, an outcome and at least one criterion")
        if implementer and implementer not in EXECUTORS:
            raise ValueError("unknown implementer")
        return self.home.get(service).new_item(title.strip(), type, outcome.strip(), criteria, implementer).id

    def act(self, service: str, item_id: str, action: str, feedback: str = "", risk: str = "") -> dict[str, Any]:
        item = self.home.get(service).item(item_id)
        if action == "stop":
            killswitch.engage(self.home.root, "stopped from the UI")
        elif action == "unstop":
            killswitch.release(self.home.root)
        elif action == "risk":
            if item.approval() or not item.plan() or risk not in ("low", "medium", "high"):
                raise ValueError("risk can only be changed on a plan that is not yet approved")
            item.set_risk(risk)
        elif action in ("start", "continue"):
            self.queue.submit(item)
        elif action in ("approve", "changes", "reject"):
            if self.queue.busy(item) or line.status(item)["status"] != "waiting":
                raise ValueError("this work item is not waiting for a decision")
            guide = guides.load(Path(item.instance.repo) / item.instance.guide)
            item.decide({"approve": "approved", "changes": "revise", "reject": "rejected"}[action], feedback, guide.version)
            self.queue.submit(item)
        else:
            raise ValueError(f"unknown action: {action}")
        return {"ok": True}


def handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: Any) -> None:
            pass

        def _send(self, code: int, body: bytes, kind: str = "application/json") -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, data: Any, code: int = 200) -> None:
            self._send(code, json.dumps(data).encode())

        def do_GET(self) -> None:
            path, _, query = self.path.partition("?")
            params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
            try:
                if path in ("/", "/index.html"):
                    self._send(200, UI.read_bytes(), "text/html; charset=utf-8")
                elif path == "/api/state":
                    self._json(app.state())
                elif path == "/api/files":
                    self._json(app.files(params["service"], params.get("item") or None))
                else:
                    self._json({"error": "not found"}, 404)
            except Exception as error:
                self._json({"error": f"{type(error).__name__}: {error}"}, 400)

        def do_POST(self) -> None:
            if self.headers.get("Origin") and self.headers.get("Host") not in (self.headers["Origin"].split("//", 1)[-1],):
                return self._json({"error": "cross-site request refused"}, 403)
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                if self.path == "/api/services":
                    self._json({"id": app.add_service(body["name"], body["repo"], body.get("implementer", "Codex"))})
                elif self.path == "/api/items":
                    self._json({"id": app.new_item(body["service"], body["title"], body.get("type", "Feature"), body["outcome"],
                                                   body["criteria"], body.get("implementer"))})
                elif self.path == "/api/act":
                    self._json(app.act(body["service"], body["item"], body["action"], body.get("feedback", ""), body.get("risk", "")))
                else:
                    self._json({"error": "not found"}, 404)
            except Exception as error:
                self._json({"error": f"{type(error).__name__}: {error}"}, 400)

    return Handler


def serve(home: Home, port: int = 8765, queue: Queue | None = None) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", port), handler(App(home, queue)))
    return server
