---
name: implement-phase
description: Use when building one phase of an approved plan, to make that phase's change and nothing else.
---

# Implement phase

Deliver exactly the phase you were given, in a working state, so the engine can checkpoint it.

## Do

1. Read the approved plan and the phase you have been given. Build only that phase.
2. Open the files involved and read the surrounding code before changing it.
3. Make the change in the smallest edit that does the job.
4. Run the quick checks for the area yourself and fix what you broke.
5. Reread your diff. Remove anything the phase did not need.
6. End your reply with `STATUS: complete` and a short list of what you changed, or `STATUS: blocked` and the reason.

## Good output

- The phase's change is present and the code still builds and its tests still run.
- The diff contains only what this phase needed.
- Your final message says which files changed and why.
- If the phase needed no change because an earlier phase covered it, you say so plainly.

## Avoid

- Building later phases early, or tidying code the plan did not mention.
- Committing. The engine commits a checkpoint when you finish.
- Ending with `STATUS: complete` when checks you ran are failing.
- Asking a question and waiting. Nobody can answer during this step; decide within the plan or report blocked.
- Changing the plan's scope on your own. Use flag-scope-change.
