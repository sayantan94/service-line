---
name: repair-in-scope
description: Use when repairing after a failed verification, to fix the diagnosed cause without leaving the approved plan.
---

# Repair in scope

Make the smallest change that removes the cause, inside what was approved.

## Do

1. Start from the cause you diagnosed. If you have not written it down, go back and do that.
2. Make the smallest edit that removes the cause.
3. Rerun the check that failed and confirm it passes for the right reason.
4. Rerun the other quick checks to confirm you broke nothing else.
5. Address every finding the verifier listed, or say why one does not apply.
6. If the fix needs work outside the approved plan, stop and report it.
7. End with `STATUS: complete` and what you changed and why, or `STATUS: blocked` and the reason.

## Good output

- The failing check now passes and the others still pass.
- The diff from the repair is small and clearly tied to the cause.
- Your final message links each change to the finding it answers.

## Avoid

- Rewriting the approach during a repair. That is a new plan.
- Weakening, skipping or deleting the check that failed.
- Fixing only the first finding. There are at most two repairs.
- Claiming complete without rerunning the failed check.
