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
├── learning/lessons.md
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

**Failure or correction → candidate lesson → validation or human review → reuse**

Store each retained lesson with its source work item, evidence, scope, and review
status. Retrieve relevant lessons during future planning. The customer can inspect,
edit, disable, or supersede them.

Session context explains current work. Instance lessons inform later work. Lessons
cannot weaken required checks, bypass approval, or silently modify an active plan.
They remain local to the instance; there is no proposed shared training pipeline.
