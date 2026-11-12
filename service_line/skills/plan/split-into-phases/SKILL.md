---
name: split-into-phases
description: Use while planning to break the work into small phases that can each be built, checked and committed on their own.
---

# Split into phases

Let the implementer make progress in small safe steps, with a working checkpoint after each.

## Do

1. List the changes the plan requires.
2. Group them into phases where each phase leaves the code building and its existing tests passing.
3. Order the phases so each builds on the last. Put the test that reproduces a bug before the fix.
4. Keep each phase to one idea: one function, one behaviour, one migration. If a title needs "and", split it.
5. Write each phase as `<short title>: <what it does>` on one line.
6. Aim for two to five phases. A one-line change is one phase; do not invent more.
7. List them under the `PHASES:` line as a numbered list, one phase per line.

## Good output

- Each phase can be described in one sentence and verified on its own.
- No phase depends on a later one.
- The last phase leaves the work ready for the engine's checks; verifying is not itself a phase unless it changes files.
- The number of phases matches the size of the work.

## Avoid

- A phase that changes nothing, such as "run the tests" or "review the change". The engine and the verifier do those, and a phase with no change looks like a stuck agent.
- One giant phase for a multi-part change.
- Phases that leave the code broken until a later phase lands.
- Putting cleanup or refactoring in as extra phases.
