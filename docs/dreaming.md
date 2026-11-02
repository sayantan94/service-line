---
layout: docs
title: Dreaming
section: dreaming
permalink: /docs/dreaming/
---

# Dreaming

**Dreaming is background synthesis of history into memory that remains useful
as context changes.** It connects facts across sessions, revises retained context,
and accounts for what is relevant now. Its output can include project facts,
preferences, constraints, decisions, and lessons.

For Service Line, it is a background maintenance workflow for one service. The
customer selects Codex or Claude to perform the analysis. Service Line controls
the inputs, evaluation, review, and publication of the resulting memory.

The general concept is memory synthesis. Isolated verification, human approval,
versioned publication, and promotion into skills are Service Line's design choices;
they are not requirements that define every dreaming system.

> This page defines the proposed runtime behavior. Dreaming, persistent memory,
> and its evaluation workflow are not implemented in the current prototype.

[Concept](#why-it-exists) · [Time](#time-changes-what-is-current) · [Lifecycle](#the-lifecycle) ·
[Example](#an-appliedin-example) · [Evaluation](#how-to-test-a-memory-change) ·
[Operation](#when-to-run-it)

## Why it exists

While solving a task, an agent gathers facts about the repository, tries approaches,
encounters failures, and receives corrections. Much of that experience is useful
beyond the current task. Without deliberate retention, a later session has to
discover it again.

An explicit saved note captures a selected fact. Dreaming can also synthesize
context that emerged naturally across sessions, without a separate instruction
to remember every detail. For this service, an inferred preference remains a
candidate until reviewed; it never overrides an explicit customer instruction.

Saving every transcript preserves the record, but leaves later agents to search
through repeated attempts, temporary assumptions, and obsolete details. A short
session summary helps resume that task; it may not connect related information
across tasks or distinguish a past constraint from a current one.

Dreaming asks a different question: **What should change about how this service
handles future work, given the evidence we now have?**

For example, separate runs might each record a timeout, a retry, and a duplicate
submission. Reviewing them together can suggest a reusable retry rule and a
regression check. That suggestion still needs validation. Repeated observations
can reveal a pattern without establishing its cause.

## What the name means

The sleep analogy refers to consolidating experience between periods of active
work. It does not imply consciousness, imagined experiences, or human sleep stages.
A dreaming job runs ordinary model calls, file operations, and configured checks.

This workflow does not update model weights. Future behavior can improve because
a later session receives better context: relevant facts, known failure modes, and
useful procedures. Improvement is a result to measure, not a property guaranteed
by the name.

| Mechanism | Its purpose |
|---|---|
| **Session checkpoint** | Record where one task stopped and what happens next. |
| **Context compaction** | Condense a long conversation so work can continue within the context window. |
| **Saved note** | Retain a selected fact or instruction, which may later need updating. |
| **Retrieval** | Find stored information relevant to the current request. |
| **Dreaming** | Reconsider retained knowledge across past work and propose a better memory store. |
| **Skill** | Describe a repeatable procedure with inputs, steps, expected results, and failure handling. |
| **Model training** | Change model parameters through a separate training process. |

These mechanisms work together. Dreaming proposes changes to what is stored;
retrieval selects what a future session needs; a skill describes how to act on
reviewed knowledge. More retained text, or a shorter summary, is not by itself
evidence of better memory.

## Time changes what is current

A memory needs a time and scope, not just a sentence. The passage of time can
make a statement obsolete even when no new message arrives. Service Line should
record when a fact was observed, when it applies, and when it needs rechecking.

| Recorded context | Later treatment in Service Line |
|---|---|
| A release window is scheduled for November 5. | After the window, retain the schedule as history; check run state before saying a release happened. |
| Staging is unavailable until 14:00. | At 14:00, recheck availability. Do not assume that it recovered. |
| Use a temporary test command for branch X. | Retrieve it only for that branch and the revisions where it was validated. |
| Prefer small PRs for this service. | Keep the reviewed preference until corrected or superseded, within its stated scope. |

Separate **planned**, **observed**, **inferred**, and **historical** information.
A due date passing changes a plan's temporal status; completion still requires
authoritative evidence. Timestamps and automatic expiry do not establish truth.

Apply validity rules when retrieving memory, even if the next dreaming job has
not run. An expired entry can remain inspectable without being supplied as current
guidance. If a validity change affects active work, surface it for a decision.

## Two loops

During active work, the executor reads approved memory, follows the approved plan,
records evidence, and writes candidate observations. Its immediate responsibility
is the current work item.

In the background, dreaming reviews stable checkpoints, retained memory, and
their time and version context. It can run while unrelated work continues. It
produces a proposed memory revision. Only an approved revision becomes
available to future work. The existing memory stays usable throughout.

<div class="concept-diagram whiteboard-diagram" role="region" tabindex="0" aria-label="Dreaming whiteboard diagram; scroll horizontally if needed" markdown="1">

![Whiteboard: history, current memory, time, and versions feed background synthesis of candidate facts, preferences, context, and lessons. Service Line validates and reviews changes before publishing versioned memory. Later work retrieves relevant, still-valid entries and produces new evidence. Rejected changes leave current memory unchanged.](assets/dreaming-whiteboard.png)

</div>

[Open the whiteboard image](assets/dreaming-whiteboard.png) ·
[Editable diagram](assets/dreaming-whiteboard.svg)

## The lifecycle

### 1. Select and snapshot inputs

Choose checkpoints relevant to one service and a defined question: current project
context, changed preferences, expiring constraints, or recurring failures. Include
decisions, corrections, successful repairs, and unresolved cases. Failure analysis
is one use of dreaming, rather than its entire purpose.

Record the input memory version, selected run and session IDs, code revisions,
verification-guide versions, the evaluation time, and evidence references. Exclude
unrelated history and sensitive values that have no role in the lesson. Read stable snapshots;
do not collect a moving view of sessions that are still writing.

### 2. Extract observations

Separate what happened from what an agent believed happened. A command's recorded
result, a state assertion, or a human correction carries different information
from an untested explanation in a transcript.

A useful observation includes the condition, action, outcome, and source. For
example: “After a simulated timeout, retrying this submission produced a second
record.” “The retry system is broken” loses the conditions needed to investigate it.

### 3. Synthesize candidate changes

Group related observations and compare them with existing memory. Propose changes
that have a clear scope and a reason to help later work.

| Proposed change | When it is useful |
|---|---|
| **Add a lesson** | Evidence establishes a new fact or failure condition. |
| **Refresh project context** | A reviewed decision or verified project change makes the retained description outdated. |
| **Update a preference** | A customer corrects a previously retained preference or its scope. |
| **Merge lessons** | Several notes describe the same rule and can share their evidence. |
| **Narrow a lesson** | A rule applies only to a particular component, environment, or version. |
| **Supersede a lesson** | New verified behavior replaces an older assumption. |
| **Retire a lesson** | The relevant code or workflow no longer exists. |
| **Recheck time-bound context** | A validity boundary has passed; mark the old context historical or unknown until checked. |
| **Propose a skill** | A validated procedure is useful across recurring tasks. |
| **Keep a question open** | Evidence is missing or contradictory. |

An empty diff is a valid outcome. Dreaming should not manufacture a lesson to
justify having run. The newest note does not automatically win a contradiction;
compare authority, conditions, code versions, and supporting evidence.

### 4. Validate the candidate

Use a separate verification session to test technical claims and procedures in
an isolated checkout. The consolidating session proposes the lesson; it cannot
establish correctness by repeating its own explanation.

Apply the relevant service checks: regression tests, controlled traffic replay,
browser journeys, logs, and state assertions. Verify both the intended outcome
and important cases where the new advice should not apply. Missing evidence
leaves the candidate unvalidated.

Generated scenarios can help test a hypothesis. They are synthetic test inputs,
not evidence that the scenario occurred in past work.

A preference such as a naming convention needs explicit customer review. A claim
that a retry is safe needs technical evidence. Do not invent a test to validate a
preference or treat a preference as proof of technical correctness.

### 5. Review the exact memory diff

Show what will be added, changed, or retired; where the evidence came from; the
scope of the advice; and the evaluation result. A human can approve, edit, reject,
or defer the candidate. Material edits to technical advice require validation again.

Learning does not rewrite customer instructions or lower the service's quality
bar. Changes to project rules, verification requirements, code, or an active plan
follow their existing approval process.

### 6. Publish a version

Create a new approved memory snapshot and update the active version only after
checking that the input version is still current. If another job published in
the meantime, reconcile the changes and review the resulting diff again.

Keep source histories, validation evidence, and previous versions. Failed,
canceled, rejected, or partially completed jobs leave the active memory unchanged.
Their drafts may remain available for inspection, clearly marked as inactive.

### 7. Retrieve and observe

Future runs read the memory index and select entries matching their task, code
area, environment, checkout, and current time. They record the memory version and
entries used. They do not load the entire archive into every prompt.

Track whether the advice was retrieved, followed, and helpful. A lesson that was
never retrieved has a different problem from one that was followed and caused
a regression. New outcomes become evidence for later consolidation.

## An AppliedIn example

Consider a hypothetical set of submission failures:

| Evidence | What it suggests |
|---|---|
| A request times out, but the application record exists. | A timeout does not establish that submission failed. |
| A later retry creates another record. | This retry path may repeat a completed operation. |
| A repair prevents duplicates in controlled tests. | The repaired behavior is a candidate for a reusable lesson. |

Dreaming could propose: “For this submission path, reconcile the existing result
before retrying, and preserve the operation's idempotency identity.” That scope
matters. It does not establish a universal rule for every external application site.

Validate with fixtures covering a timeout after a successful write, a timeout
before any write, and repeated or concurrent requests. Use the browser to check
recovery and status, then assert that the persisted state contains the expected
single application. A screenshot alone cannot prove the database outcome.

After validation and review, retain the lesson. If the procedure proves useful
across representative tasks, propose a retry-verification skill with setup,
actions, assertions, and failure handling. Updating required verification checks
still requires approval of the service's guide.

A later feature involving retries can retrieve this lesson while planning and
include the relevant checks before implementation. That is the expected benefit:
the next work item accounts for a previously discovered failure earlier.

## What retained memory contains

Facts, preferences, project context, and lessons need different validation, but
share a record that can be understood and challenged without reopening every
source transcript.

| Field | Purpose |
|---|---|
| Identity and status | Stable ID; candidate, approved, superseded, or disabled. |
| Kind and basis | Fact, preference, decision, plan, or lesson; explicitly stated, observed, or inferred. |
| Claim and recommended action | The fact or procedure future work should consider. |
| Applicability | Service, component, conditions, and relevant code or environment versions. |
| Time and validity | When observed, when applicable, the last check, and any expiry or recheck condition. |
| Exceptions | Cases where the advice is unsafe, unnecessary, or unproven. |
| Sources | Work items, runs, sessions, corrections, and evidence artifacts. |
| Validation | Checks performed, tested revision, results, and unresolved limits. |
| Review | Who approved the exact content and which version was approved. |
| Lifecycle | Creation, later use, revalidation, and any replacement lesson. |

Store the concise entry in the memory collection and link to detailed evidence.
Repeated copies of one claim are not independent corroboration. Preserve the
distinction between observed facts, interpretations, and open questions.

## Inspecting and correcting memory

Show a compact summary of the service's current context, constraints, preferences,
and lessons, with an update time and links to the underlying records. A summary
is a view of retained memory; it is not an exhaustive list or the source of truth.

The customer should be able to inspect why an entry was retained, correct its
scope, disable its future use, or request removal. Disabling an entry and deleting
its source history are separate operations. Track exclusions so a later batch
does not silently recreate a removed entry from unchanged source material.

Revalidate technical corrections before publication. An owner-confirmed preference
does not require a fabricated test. Keep historical run evidence under its own
retention policy, and make any retained copies clear to the customer.

## How to test a memory change

Correct advice is necessary, but it may still be irrelevant, too broad, or too
expensive to load. Evaluate both correctness and its effect on future work.

| Memory objective | A Service Line evaluation case |
|---|---|
| **Carry useful context forward** | A new session identifies a previously agreed API compatibility constraint without being told again. |
| **Respect preferences and constraints** | A plan follows the reviewed service preference for small changes, while still satisfying required checks. |
| **Stay current** | Run the same question before and after a staging restriction expires; the later answer requests a fresh availability check. |

Also test irrelevant memories, explicit corrections, contradictions, and removed
entries. Use histories with known event order and an injected clock. Score whether
the resulting answer or action uses valid context, not just whether a phrase was
retrieved. Planned-but-unconfirmed work must never become a claimed completion.

For a meaningful comparison, use the same repository revision, task, executor
settings, tool permissions, verification criteria, and execution budget. Compare
the approved memory with the candidate memory in isolated runs. Include related
cases that were not used to create the lesson; repeating the source example alone
does not test whether the lesson generalizes.

Compare completion rate, repeated failures, repair attempts, human corrections,
time, and token cost. Look for regressions on neighboring tasks. Agent behavior
can vary between runs, so use repeated trials where the decision warrants them
and report the sample size and uncertainty. Do not claim a productivity gain from
one successful replay.

The candidate cannot improve its score by changing the evaluator, weakening checks,
or increasing permissions. If it fails, narrow it, gather more evidence, or leave
it inactive. Continue monitoring after publication and roll back harmful memory.

## When to run it

Start with an explicit **Review learning** action over selected completed runs.
Later, offer a configurable trigger after a batch of work, repeated failures, a
significant correction, a validity boundary, or a scheduled interval. A date or
environment version change can justify refreshing context without new messages.
Skip work only when both the inputs and their applicability remain unchanged.

Bound the input range, runtime, token use, and validation work. Save checkpoints
for long jobs. Group observations by topic when the history is too large for one
context window, retaining source links through every summary.

Refresh affected topics incrementally and periodically check older entries that
remain eligible for retrieval. Keep the model's input bounded while preserving
references to the full record. Measure memory quality and compute cost on this
service before expanding the job's scope.

Dreaming consumes resources. Measure its analysis and evaluation costs alongside
any savings in later work. Avoid running it after every tool call or repeatedly
processing unchanged inputs.

## Ownership and concurrent work

Sessions write separate candidates. A consolidation job writes to its own staging
folder. A single publisher per instance installs an approved version atomically;
ordinary work sessions cannot edit the approved store.

Active runs retain the memory version and plan they started with, while checking
time and environment validity before using an entry. If a new lesson
reveals a problem in active work, surface it for an explicit decision and revised
plan where needed. Do not silently replace its context mid-run. Rollback changes
what future runs load and preserves the audit trail.

Treat retrieved pages, logs, and transcript text as evidence to assess. Embedded
instructions in that material do not become authority because they were saved in
memory. A lesson cannot grant tools, credentials, or permissions. Keep memory
scoped to its service and review any copy into another service.

The files remain in the instance's working folder. The selected executor receives
the context required for analysis, so local storage alone does not imply offline
processing.

## Fit within Service Line

Dreaming uses the same six primitives. The **instance** owns memory. A maintenance
**work item** defines the learning scope. Its **workflow** coordinates analysis,
validation, and review. The chosen **executor** performs the work in separate
analysis and verification **sessions**. A **run** records snapshots, cost, state,
and evidence.

The learning work item's plan defines allowed sources, checks, and budget under
the normal approval process. Publication is a separate review of the resulting
memory diff. No additional top-level primitive is required.

The first implementation should support a small manual batch, a visible candidate
diff, independent validation, human publication, versioned retrieval with validity
checks, and rollback.
Scheduling can follow once that complete loop works. Automatic publication is
outside this initial design.

[Context and learning](context-and-learning.md) covers the filesystem layout and
session handoff. [Verification](verification.md) defines how results become
evidence for review.
