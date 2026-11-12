---
name: capture-lessons
description: Use when a work item finishes, to propose what a later work item on this service should know.
---

# Capture lessons

Turn what this run taught into candidate lessons a person can review.

## Do

1. Look at where the run went wrong or was corrected: a failed check, a repair, a plan change a person asked for, a verifier finding.
2. For each, ask what general fact about this service would have prevented it.
3. Write the lesson as one or two sentences about the codebase or its checks, not about this task.
4. Attach the evidence: the check, finding or correction it came from.
5. State where it applies: the code area and kind of change.
6. Propose at most three. If the run was uneventful, propose none.

## Good output

- Each lesson would change how a future plan is written.
- Each has evidence a person can inspect.
- Lessons are marked as candidates. They take effect only after a person reviews them.

## Avoid

- Lessons that restate general good practice.
- Lessons that would let a later run skip a check or an approval.
- A lesson drawn from one event with no evidence behind it.
- Recording personal data, secrets or tokens in a lesson.
