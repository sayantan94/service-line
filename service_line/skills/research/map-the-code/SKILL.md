---
name: map-the-code
description: Use at the start of a work item to find every file, test and setting the request touches before anything is planned.
---

# Map the code

Give the planner an accurate map of the code involved, so the plan is built on what the repository actually contains.

## Do

1. Restate the request in one sentence, in the repository's own terms (the function, endpoint, screen or job it concerns).
2. Search for the behaviour, not just the words: entry points, callers, the data it reads and writes, and configuration that switches it.
3. Open each candidate file and confirm it is really involved. Record the path and the specific function or section.
4. Follow the call chain one level out in each direction: who calls this, and what does it call that could break.
5. Find the tests that already cover this area and note how they are run.
6. List what you could not determine and what would settle it.

## Good output

- A short list of files with exact paths, each with one line on its role in this request.
- The existing tests for the area, with the command that runs them.
- Callers and dependents that a change here could affect.
- An explicit list of unknowns. An honest unknown is more useful than a confident guess.

## Avoid

- Proposing a solution. Research describes what is there; the plan decides what to do.
- Listing files because their names match. Open them first.
- Editing anything, or running commands that change state. This step is read-only.
- Summarising the whole repository. Only what this request touches matters.
