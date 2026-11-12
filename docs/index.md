---
layout: docs
title: Overview
section: overview
permalink: /docs/
---

# Service Line

A software factory for bugs, features, refactors, maintenance, and new products.
The customer chooses the executor and approves the plan. Service Line coordinates
the work, requires evidence, and retains useful context locally.

> This repository contains an interactive prototype and a proposed architecture.
> It does not run agents, execute tests, replay traffic, or change product repositories.

## The factory line

<ol class="flow"><li>Intake</li><li>Plan</li><li>Approval</li><li>Implement</li><li>Verify</li><li>Ready</li></ol>

Each service has a floor in the spatial Factory view. Select a workstation to
inspect its work, or switch to the line to follow each stage. Open an item to
review its plan, sessions, changes, and evidence. A failed check returns it to
repair. Missing evidence stops progress. Ready means ready for review.

The design adds three loops around this line. One observes a change after
deployment, one scans the repository on a schedule and proposes work, and one
learns from past work. The prototype shows the line only.

[Open the mock UI](../service-line-ui.html)

![The stage-by-stage board in the interactive prototype](assets/factory-line.png)

## Start with the model

- [Primitives](primitives.md): the six objects and what each owns.
- [Workflow](workflow.md): the four loops, risk levels, approval, repair, and resumption.
- [Verification](verification.md): browser actions, replay, observations, gates, and
  post-deploy signals.
- [Context and learning](context-and-learning.md): session memory and reusable lessons.
- [Dreaming](dreaming.md): how past work becomes validated guidance for future runs.
- [Try the prototype](getting-started.md): the controls and current limits.

The expected benefit is less repeated explanation and manual coordination.
Approved work can proceed through checks and repairs while the customer focuses
on scope, decisions, and results. Productivity gains remain to be measured once
the runtime exists.
