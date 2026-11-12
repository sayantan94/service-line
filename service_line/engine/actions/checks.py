import json

from .common import RunEnv

CHECK_TIMEOUT = 900


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    """An engine step: no agent runs or reports these."""
    attempt = ctx.get("checks", {}).get("attempt", 0) + 1
    head = env.checkout.head()
    results = []
    for check in env.guide().checks:
        started = env.log.start("check", id=check.id, command=check.command)
        done = env.checkout.run(["/bin/sh", "-c", check.command], mode="workspace-write", timeout=CHECK_TIMEOUT)
        env.log.end("check", started, "timeout" if done.timed_out else "completed", exit_code=done.exit_code)
        output = env.save(f"attempt-{attempt}/{check.id}.txt", f"$ {check.command}\n\n{done.output}\nexit: {done.exit_code}\n")
        results.append({"id": check.id, "command": check.command, "exit_code": done.exit_code,
                        "timed_out": done.timed_out, "output": output})
    env.checkout.reset(head)        # checks must not change the code they check
    env.save(f"attempt-{attempt}/checks.json", json.dumps({"revision": head, "results": results}, indent=2))
    return {"attempt": attempt, "revision": head, "results": results}
