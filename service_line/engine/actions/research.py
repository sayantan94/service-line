from .common import RunEnv, describe


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    result = env.agent("Research", f"{describe(env.item)}\n\nResearch this request in the repository. Report the files involved, "
                       "the conventions that apply, the existing tests, and what is unknown. Do not change anything.")
    return {"notes": env.save("research.md", result.output)}
