---
name: self-check
description: Use before finishing a phase, to catch your own mistakes while they are cheap to fix.
---

# Self check

Hand over work that already passes the checks you can run yourself.

## Do

1. Run the fastest relevant check for the area: the focused test, the type check, or the linter.
2. Read the output fully. A warning you introduced counts.
3. Fix failures you caused. Rerun until clean.
4. Reread the whole diff as a reviewer would: unintended edits, leftover debugging, missing cases.
5. Check the phase against the plan: did you do what it said, and only that?
6. State in your final message which checks you ran and their result.

## Good output

- The checks you ran are named with their outcome.
- Any failure you could not fix is reported, with what you tried.
- The diff is free of stray changes.

## Avoid

- Reporting success without running anything.
- Hiding or disabling a failing check.
- Treating a failure that existed before your change as yours to hide. Report it as pre-existing.
- Running the slowest full suite when a focused check would do; the engine runs the full checks next.
