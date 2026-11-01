---
layout: docs
title: Workflow
section: workflow
permalink: /docs/workflow/
---

# From request to verified change

1. **Intake.** Record the outcome and acceptance criteria.
2. **Plan.** Read repository instructions and relevant lessons. Propose the scope,
   approach, and checks using the selected executor.
3. **Approval.** A human approves the exact plan and verification requirements.
4. **Implement.** Work in the item's isolated checkout and checkpoint the session.
5. **Verify.** Run required checks and a separate verification session. Record evidence.
6. **Ready.** Present the change and evidence for review. Merge and deployment are
   separate actions.

## Approval and repair

Approval binds the plan version, verification-guide revision, and resolved check
configuration. The engine validates that decision before implementation starts.

| Outcome | Next action |
|---|---|
| Required evidence and reviews pass | Ready for review |
| An assertion fails | Repair within the approved scope, then verify a new snapshot |
| Evidence is missing or inconclusive | Needs attention; no pass |
| Scope or required checks change | Revise the plan and obtain approval again |
| Repair limit is reached | Stop for a human decision |

Human acceptance remains explicit for criteria assigned to a person.

## ASL-style definitions

Definitions live in `workflows/`. Each run pins a version. `Task` dispatches an
action, `Choice` routes a result, and terminal states end a run. Custom actions
provide planning, approval waits, execution, verification, and repair.

[Read the proposed software-change workflow](../workflows/software-change.asl.json).
This is a design example; no interpreter or hosted workflow service is included.
The approval action waits for a human; implementation checks that approval still
matches the plan. The repair action returns the full run context with an incremented
`repairs` count and a new code snapshot. Verification checks explicit human
acceptance when required. Errors without a recovery route halt the run.

Transport retries and code repair are different. A retry must not repeat an
unknown external side effect. Code repair follows a failed assertion and consumes
the work item's repair budget.

## Resume

Persist structured state before and after actions. On restart, reconcile any
in-flight operation, verify the checkout against its checkpoint, and resume the
existing session when supported. Do not blindly repeat an action whose outcome
is unknown. These runtime guarantees are proposed, not implemented in the mock UI.
