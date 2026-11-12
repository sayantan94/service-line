from .common import RunEnv, describe
from .implement import build


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    """Returns the whole run context with one more repair counted."""
    plan = env.item.plan()
    failed = [r for r in ctx.get("checks", {}).get("results", []) if r["exit_code"] != 0]
    outputs = "\n\n".join((env.run_dir / r["output"]).read_text()[-3000:] for r in failed) or "(no check failed)"
    findings = ctx.get("review", {}).get("findings")
    review = (env.run_dir / findings).read_text()[-3000:] if findings else "(none)"
    number = ctx.get("repairs", 0) + 1
    base = ctx["implementation"]["base"]

    def task(_: int, __: str) -> str:
        return (f"{describe(env.item)}\n\nApproved plan:\n{plan['text']}\n\nVerification failed. This is repair {number} of 2.\n\n"
                f"Failed checks:\n{outputs}\n\nVerifier findings:\n{review}\n\n"
                "State the cause first, then fix it inside the approved plan. "
                "End with `STATUS: complete` and what you changed, or `STATUS: blocked` and why.")

    head = build(env, "Repair", base, task, [f"repair {number}"])
    return {**ctx, "repairs": number, "implementation": {**ctx["implementation"], "revision": head,
                                                         "changed": env.checkout.changed_files(base)}}
