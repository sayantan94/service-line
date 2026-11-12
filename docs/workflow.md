---
layout: docs
title: Workflow
section: workflow
permalink: /docs/workflow/
---

# From request to verified change

1. **Intake.** Record the outcome and acceptance criteria.
2. **Plan.** The implementer researches the code, repository instructions, and
   relevant lessons, then proposes the scope, phases, checks, and a risk level.
   The verifier reviews the plan and attaches its findings.
3. **Approval.** A human approves the exact plan, risk level, and verification
   requirements.
4. **Implement.** Work in the item's isolated checkout, one plan phase at a time,
   and commit a checkpoint after each phase.
5. **Verify.** The engine runs the required checks. The verifier, a different
   executor, exercises the service and reviews the change. Record evidence.
6. **Ready.** Present the change and evidence for review. Merge and deployment are
   separate actions.

## Steps inside each stage

The board shows six stages. The workflow runs more steps than that, and each step
is run by an agent, by the engine, or by you.

| Stage | Step | Run by |
|---|---|---|
| Intake | State the outcome and acceptance criteria | You |
| | Create the work item and its checkout | Engine |
| Plan | Research the code, rules, and lessons | Implementer |
| | Write the plan: scope, phases, checks, risk level | Implementer |
| | Review the plan | Verifier |
| Approval | Approve, revise, or reject | You |
| | Bind the plan, risk level, guide version, and check list | Engine |
| Implement | Build one phase, self-check, commit a checkpoint | Implementer |
| Verify | Format, lint, build, and required checks | Engine |
| | Exercise the service, run hidden scenarios, review the diff | Verifier |
| | Evaluate the evidence | Engine |
| Ready | Review the evidence, then merge and deploy | You |

The implementer is the executor the customer chose. The verifier is the other
one. Engine steps are fixed code: an agent cannot run them or report their
result. [Runtime](runtime.md) describes how the engine enforces this.

## Four loops

The six stages are one loop. A factory that only checks a change before review
misses what happens after it ships and what decays while nobody is looking.

| Loop | Runs | Purpose | Definition |
|---|---|---|---|
| **Change** | For each work item | Plan, approve, implement, verify, and repair until Ready. | `software-change` |
| **Observe** | After a recorded deployment | Check that the shipped change behaves as the plan expected. | `post-deploy-observe` |
| **Maintain** | On a schedule | Scan the repository and propose work items for what it finds. | A scheduled maintenance work item |
| **Learn** | Between work items | Turn past work into reviewed context and lessons. | [Dreaming](dreaming.md) |

Each loop feeds the others. Observations and scan findings arrive as new work
items at Intake. Their evidence becomes input to dreaming, and published lessons
inform the next plan. All four use the same six primitives.

## Risk sets the depth

Every plan states a risk level and the reasons for it: how much code and data the
change can affect, which other services depend on it, whether it touches
security-sensitive paths, and how easily it can be reversed.

| Risk | Verification | Human review at Ready | Observe loop |
|---|---|---|---|
| **Low** | Required checks from the service guide and the verifier's review. | Evidence summary. | Optional |
| **Medium** | Adds security review and checks on dependent callers. | Diff and evidence. | Optional |
| **High** | Adds the full browser and replay journeys and checks in dependent services. | A named reviewer records acceptance. | Required |

These are defaults. The service guide lists the checks each level requires.
The approver can raise or lower the proposed level before approving. Changing it
afterwards is a scope change and needs approval again. The engine raises the level
when the implemented change reaches outside the approved scope; it never lowers it.

Risk decides how much verification and review a change receives. It does not
decide whether a human approves the plan: every level keeps plan approval.
Automatic approval and automatic merge are outside this design.

## Approval and repair

Approval binds the plan version, risk level, verification-guide revision, and
resolved check configuration. The engine validates that decision before implementation starts.

| Outcome | Next action |
|---|---|
| Required evidence and reviews pass | Ready for review |
| An assertion fails | Repair within the approved scope, then verify a new snapshot |
| Evidence is missing or inconclusive | Needs attention; no pass |
| Scope, risk level, or required checks change | Revise the plan and obtain approval again |
| Repair limit is reached | Stop for a human decision |
| A deployed change regresses under observation | New work item with the observation evidence; a human decides on rollback |

Human acceptance remains explicit for criteria assigned to a person.

## Observe after deployment

Ready is not the end of a change. Merge and deployment stay with people and their
pipeline. Once a deployment of the verified revision is recorded on the work item,
a second run can start with the `post-deploy-observe` workflow.

The run reads the production signals the service guide names, such as logs,
traces, metrics, and error rates, for a bounded window. It compares them with the
outcomes the approved plan expected.

| Result | Next action |
|---|---|
| Signals match the plan | Confirmed; the evidence is attached to the work item |
| Signals contradict the plan | Regressed; propose a new work item at Intake with the evidence |
| Required signals are unavailable | Needs attention; no confirmation |

Observation is read-only. It does not roll back, change a feature flag, or widen
a rollout. It reports to a human who decides.

[Read the proposed post-deploy-observe workflow](../workflows/post-deploy-observe.asl.json).

## Maintenance intake

Requests from people are one source of work. Some problems appear only after a
change has merged: a vulnerability published later, a rule adopted later, or
duplication and complexity that build up across many small changes.

A scheduled maintenance work item covers these. Its plan is approved once and
defines the scan scope, checks, schedule, and budget. Each run scans the
repository and records findings with their source evidence. It merges duplicates
and proposes each remaining finding as a candidate work item at Intake.

A human accepts or rejects each candidate. Accepted items follow the normal line,
including plan approval. A scan does not edit product code.

## ASL-style definitions

Definitions live in `workflows/`: `software-change` for the change loop and
`post-deploy-observe` for the observe loop. Each run pins a version. `Task` dispatches an
action, `Choice` routes a result, and terminal states end a run. Custom actions
provide research, planning, plan review, approval waits, execution, checks,
verification, and repair.

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

Each run keeps one append-only log, synced to disk before every agent call and
every command. On restart the engine closes any step left open. A step where
nothing had started is run again. A step whose agent call or command had started
but not finished has an unknown outcome: the engine resets the checkout to the
last checkpoint before running it again. It never continues on a half-changed
checkout. [Runtime](runtime.md#recovery-after-a-crash) has the details. These runtime guarantees are proposed, not implemented in the mock UI.
The mock UI shows risk levels and the two executors with sample data. It does not
simulate the observe loop or maintenance scans.
