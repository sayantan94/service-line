"""Command line for Service Line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import line
from .policy import killswitch
from .queue import Queue
from .server import App, serve
from .store.instances import Home


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="service-line", description="A software factory engine.")
    parser.add_argument("--home", help="folder that holds the services (default: ./instances or $SERVICE_LINE_HOME)")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("serve", help="start the local server and the UI")
    s.add_argument("--port", type=int, default=8765)
    a = sub.add_parser("add-service", help="register a repository as a service")
    a.add_argument("name"); a.add_argument("repo"); a.add_argument("--implementer", default="Codex", choices=("Codex", "Claude"))
    n = sub.add_parser("new-item", help="create a work item")
    n.add_argument("service"); n.add_argument("title"); n.add_argument("--type", default="Feature")
    n.add_argument("--outcome", required=True); n.add_argument("--criterion", action="append", required=True)
    for name, text in (("start", "start or continue a work item"), ("approve", "approve the current plan and continue"),
                       ("reject", "reject the current plan")):
        p = sub.add_parser(name, help=text); p.add_argument("service"); p.add_argument("item")
    c = sub.add_parser("changes", help="ask for changes to the current plan")
    c.add_argument("service"); c.add_argument("item"); c.add_argument("feedback")
    sub.add_parser("status", help="list services and work items")
    sub.add_parser("stop", help="stop every agent before its next step")
    sub.add_parser("unstop", help="release the stop switch")
    args = parser.parse_args(argv)

    home = Home(Path(args.home) if args.home else None)
    if args.command == "serve":
        server = serve(home, args.port)
        print(f"Service Line is running at http://127.0.0.1:{args.port}  (services in {home.root})", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
        return 0
    if args.command == "status":
        for inst in home.all():
            print(f"{inst.id}  {inst.name}  {inst.repo}")
            for item in inst.items():
                where = line.status(item)
                print(f"  {item.id}  {where['status']:<16} {where.get('current') or '':<16} {item.title}")
        return 0
    if args.command == "stop":
        killswitch.engage(home.root, "stopped from the command line"); print("stop switch engaged"); return 0
    if args.command == "unstop":
        killswitch.release(home.root); print("stop switch released"); return 0
    app = App(home, Queue(home=home.root))
    if args.command == "add-service":
        print(app.add_service(args.name, args.repo, args.implementer)); return 0
    if args.command == "new-item":
        print(app.new_item(args.service, args.title, args.type, args.outcome, args.criterion)); return 0
    item = home.get(args.service).item(args.item)
    action = {"start": "start", "approve": "approve", "reject": "reject", "changes": "changes"}[args.command]
    app.act(args.service, args.item, action, getattr(args, "feedback", ""))
    app.queue.wait(item)
    where = line.status(item)
    print(f"{item.id}: {where['status']}" + (f" ({where['detail']})" if where.get("detail") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
