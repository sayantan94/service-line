---
layout: docs
title: Context & learning
section: context
permalink: /docs/context-and-learning/
---

# Keep context local

Each instance has a working folder. Each session records what was decided, what
changed, the supporting evidence, unresolved blockers, and the next step.

```text
instances/appliedin/
├── instance.yaml
├── learning/
│   ├── lessons.md
│   ├── candidates/
│   ├── consolidations/
│   └── skills/
└── workitems/WI-001/
    ├── workitem.md
    ├── plans/v1.md
    ├── approvals/v1.json
    ├── workspace/
    ├── runs/run-001/
    │   ├── state.json
    │   └── artifacts/
    └── sessions/
        ├── implementation/
        │   ├── session.json
        │   ├── context.md
        │   └── history.jsonl
        └── verification/
            ├── session.json
            ├── context.md
            └── history.jsonl
```

This is the proposed runtime layout. The prototype does not create these files.

## Session memory

`session.json` records the executor and native session reference. `context.md`
provides compact working memory; history retains the underlying events. Resume
checks the current checkout before continuing from a checkpoint.

Implementation and verification stay in separate sessions. Switching executors
starts a new native session with a recorded handoff. Markdown cannot substitute
for an approval, a tool result, or structured run state.

## Local learning loop

**Capture → consolidate → validate → review → reuse → measure**

Proposed runtime capability: Codex and Claude use the same local memory contract.
Learning changes stored context and procedures, not model weights.

### What to retain

| Material | Purpose |
|---|---|
| Repository instructions | Customer-owned rules and stable project conventions. |
| Session context and history | Decisions, attempts, corrections, and evidence for current work. |
| `learning/lessons.md` | A compact index of approved, scoped lessons for later work. |
| `learning/skills/` | Reviewed procedures for recurring tasks, with inputs, steps, and checks. |

Read the filesystem index during planning, then load entries relevant to the task
and checkout. Record the memory version and lesson IDs used. Promote repeatable
procedures into skills, subject to the service's verification guide.

### Consolidate between sessions

**Dreaming** is a background job over completed or stopped runs. Run it on demand
or on a configured schedule, with session and token limits. Use the customer's
selected executor and existing workflow, session, and run primitives.

1. Snapshot the instance's retained memory, session histories, human corrections,
   and verification evidence.
2. Identify repeated failures and successful repairs. Merge duplicates, flag
   contradictions, and propose retiring stale lessons. Keep one-off observations
   scoped to their original work until supported by evidence.
3. Write a candidate memory revision and readable diff under `learning/consolidations/`.
   Preserve the current memory and source histories.
4. Validate proposed procedures against relevant regression cases, replay fixtures,
   or browser journeys in an isolated checkout. Record missing evidence explicitly.
5. Present the diff, sources, and validation results for human review. Publish an
   approved version for future runs; rejected candidates remain inactive.

Candidates record source work items and runs, evidence, scope, proposed changes,
validation, and review status. Human preferences can be recorded directly as
candidates; technical claims require verification.

Sessions write separate candidates. One writer publishes per instance after
checking the input memory version is still current. Active runs keep their version
and approved plan. Retain older versions for inspection, disabling, and rollback.

### Example: a recurring application retry bug

If AppliedIn repeatedly encounters duplicate submissions after a timeout,
consolidation could propose an idempotency lesson and a retry-verification skill.

Validate by replaying the timeout and retry, checking browser recovery, and
asserting that only one application record exists. After review, later plans
retrieve the lesson. Changes to `service-line-verification.md` still require
normal review and approval.

### Measure whether it helps

Compare representative tasks with and without the candidate memory before
promotion. Track repeated failures, repair attempts, human corrections, completion
rate, latency, and token cost. Record regressions and disable harmful lessons.
More saved notes alone do not establish improvement.

Memory stays local to the instance. Lessons cannot weaken required checks, bypass
approval, or override customer instructions. There is no shared training pipeline.

Design input: the [memory and dreaming post](https://x.com/rdominguezibar/status/2116880535167389708),
[memory tool documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool),
and [dreaming documentation](https://platform.claude.com/docs/en/managed-agents/dreams).
The lifecycle above is Service Line's proposed design.
