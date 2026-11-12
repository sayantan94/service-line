---
layout: docs
title: Primitives
section: primitives
permalink: /docs/primitives/
---

# Six primitives

The UI calls an instance a **service**. These are two names for the same object.

| Primitive | Owns | Example |
|---|---|---|
| **Instance** | Repository reference, working folder, executor default, work items, verification configuration, local lessons. | AppliedIn |
| **Work item** | Requested outcome, acceptance criteria, versioned plan and risk level, human approval, sessions, runs. | Prevent duplicate applications |
| **Workflow** | Versioned states, actions, transitions, timeouts, and repair limits. | `software-change` |
| **Executor** | Adapter for agent invocation, native session references, tool limits, and results. A work item has two: the implementer and the verifier. | Codex or Claude |
| **Session** | Conversation for one work item and one executor, `context.md`, checkpoints, history. | Implementation session |
| **Run** | Execution of one workflow version: checkout, append-only event log, attempts, checks, artifacts, errors. | `run-001` |

## Ownership

```text
Instance
└── Work item
    ├── Plan and approval
    ├── Sessions ── each belongs to one executor
    └── Runs ────── each pins one workflow version
```

A work item can have multiple runs. Sessions can continue across those runs;
implementation and verification use separate sessions on different executors. Different work items use
isolated checkouts so concurrent changes do not share a mutable working tree.

The instance provides the default implementer. A work item can override it before
approval. The engine assigns the other executor as the verifier. Changing providers creates a new native session with an explicit
context handoff; it does not convert the previous provider's conversation.

## What does not need another primitive

States and actions belong to workflows. Checks and artifacts belong to runs.
Skills are reusable task instructions. Approval is a versioned human decision on
the work item. Lessons belong to the instance.

Risk level is part of the plan and is approved with it. Post-deploy observation
is a second run of the same work item with a different workflow. A maintenance
scan is a scheduled work item whose findings become candidate work items.

The engine owns workflow state. Markdown supplies instructions and memory; editing
`context.md` cannot approve a plan or mark a run complete.
