import re
from pathlib import Path

from .common import RunEnv, describe

FORMAT = """Reply with one line per criterion and a final verdict, in exactly this shape:

AC1: pass | fail | unknown - <evidence>
...
VERDICT: passed | failed | inconclusive"""


def parse(text: str) -> tuple[str, dict[str, str]]:
    criteria = {m.group(1).upper(): m.group(2).lower() for m in re.finditer(r"^(AC\d+):\s*(pass|fail|unknown)\b", text, re.I | re.M)}
    verdict = re.search(r"^VERDICT:\s*(passed|failed|inconclusive)\b", text, re.I | re.M)
    return (verdict.group(1).lower() if verdict else "inconclusive"), criteria


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    head = env.checkout.head()
    before = env.checkout.fingerprint()
    base = ctx.get("implementation", {}).get("base", head)
    plan = env.item.plan()
    checks = "\n".join(f"- {r['id']}: exit {r['exit_code']}" + (" (timed out)" if r["timed_out"] else "")
                       for r in ctx.get("checks", {}).get("results", [])) or "(none ran)"
    hidden = Path(env.item.instance.dir) / "hidden"          # outside the implementer's checkout
    scenarios = "\n\n".join(f"### {p.name}\n{p.read_text()}" for p in sorted(hidden.glob("*.md"))) if hidden.exists() else ""
    diff = env.checkout.diff(base)[:20000]
    result = env.agent("Review", f"{describe(env.item)}\n\nApproved plan:\n{plan['text']}\n\nEngine check results:\n{checks}\n\n"
                       f"The change to review:\n```diff\n{diff}\n```\n\n"
                       + (f"Hidden scenarios the implementer never saw. Run them:\n{scenarios}\n\n" if scenarios else "")
                       + f"You may run commands to exercise the code. You cannot edit it.\n\n{FORMAT}")
    verdict, criteria = parse(result.output)
    if env.checkout.fingerprint() != before:
        env.checkout.reset(head)
        verdict = "inconclusive"                              # a verifier that changes the code proves nothing
    if verdict == "passed" and (len(criteria) < len(env.item.criteria) or set(criteria.values()) != {"pass"}):
        verdict = "inconclusive"                              # a pass needs a pass on every criterion
    return {"verdict": verdict, "criteria": criteria, "revision": head, "findings": env.save(f"review-{head[:8]}.md", result.output)}
