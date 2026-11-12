---
layout: docs
title: Runtime
section: runtime
permalink: /docs/runtime/
---

# How the engine runs work

The engine is the only part that moves a work item forward. Agents do the
thinking inside a step. The engine decides which step runs, what the agent may
touch, and whether the result counts.

> This page is the proposed runtime design. None of it is implemented. The
> prototype shows sample data only.

[Open the runtime design](https://sayantan94.github.io/service-line/design/): one diagram with every piece, then a page each
for the parts, the steps, the run log and recovery, the agents and their limits,
verification, learning, and the loops.

## Agent steps and engine steps

Every workflow step is one of three kinds, and the kind never changes at run time.

| Kind | Run by | Examples |
|---|---|---|
| **Agent** | An executor, inside limits the engine sets | Research, plan, plan review, implement, verify, repair |
| **Engine** | Fixed code, the same every time | Create the checkout, format, lint, build, run checks, evaluate evidence |
| **Human** | You | Intake, approval, review at Ready |

Checks and the evidence gate are engine steps. An agent cannot run them, skip
them, or report their result.

## Two executors per work item

The customer chooses the **implementer**: Codex or Claude. The engine assigns the
other one as the **verifier**. The verifier reviews the plan before approval and
the change after implementation.

An agent reviewing its own work tends to miss its own mistakes. Using a second
executor gives the review different blind spots. The verifier cannot edit the
plan or the code it reviews. With only one executor installed, verification uses
a fresh session of the same one and the run records that the review was not
independent.

## The run log

Each run has one append-only log. It is the only record of what happened, and
all other state is derived from it.

```text
runs/run-001/
├── events.jsonl      # one event per line, numbered from zero
├── run.lock          # held by the engine while the run is open
└── artifacts/        # check output, captures, evidence manifest
```

An event has a sequence number, a time, a type, and data:

```json
{"seq": 14, "time": 1794470000000, "type": "step/start", "data": {"step": "Implement", "phase": 2}}
```

Rules for the log:

- **Bracket every step.** `step/start` is always followed by `step/end` with a
  reason: completed, failed, interrupted, or timed out. The end event is written
  even when the step raises an error.
- **Bracket every side effect.** An agent call or a check command is logged as
  started before it runs and as finished after it returns.
- **Sync before side effects.** The log is forced to disk before each agent call
  and each command. A start event with no finish event then reliably means the
  action may have run.
- **Derive, do not store.** The current step, repair count, approval, and verdict
  are computed by replaying events. The UI reads the same log.
- **Record what the agent saw.** Every instruction, skill, and context file handed
  to an agent is an event, so any agent call can be reconstructed afterwards.

Plans, approvals, and evidence stay as readable files. The log references them by
path and content hash.

## Durable writes

- A new log is written to a temporary file, synced, and then linked into place,
  so a second creator fails instead of overwriting.
- An append is written and synced. If the write fails, the file is truncated back
  to its previous size so a retry cannot duplicate events.
- On load, a last line with no newline is ignored and removed before the next write.
- One lock per run. The operating system releases it if the engine dies.

## Recovery after a crash

On restart the engine does not resume a step from the middle. It closes what was
open and then decides what to do next.

| What the log shows | What the engine records | Next action |
|---|---|---|
| Step started, no side effect started | Interrupted, nothing ran | Run the step again |
| Agent call or command started, no finish | Interrupted, outcome unknown | Reset the checkout to the last checkpoint, then run the step again |
| Step ended | Nothing to repair | Continue with the next step |

A retry never runs on a half-changed checkout. The implementer commits a
checkpoint after each plan phase, which gives the engine a known state to return to.

## Driving the executors

The engine drives each executor through its structured interface, not by reading
terminal output.

| Executor | Interface | What the engine controls |
|---|---|---|
| Claude | Claude Agent SDK | Working directory, permission mode, a permission callback in engine code, removed tools |
| Codex | `codex app-server` over standard input and output | Working directory, sandbox mode, approval policy, interrupt |

Both adapters follow the same contract:

- **A run always returns a result.** The result has the output, a stop reason, and
  a diagnostic. A failed agent is a result, not an exception. Exceptions are kept
  for engine faults, which stop the run.
- **Completion is strict.** A step is complete only when the executor reports
  exactly one successful result with content. An exit, a closed stream, or silence
  without that result is a failure.
- **Agents cannot ask anyone.** Unattended steps decline every approval request and
  have no tool for asking the user. A step that needs a decision ends and the run
  goes to Needs attention.
- **One way to stop.** Close input, wait briefly, signal the process group, wait,
  then kill. Every exit path uses the same sequence once.
- **A time limit per step.** The workflow sets it. When it expires the engine
  stops the executor and records a timeout.

## Limits on each step

Limits are set in engine code. Skills tell an agent how to do a step; they do not
restrict it.

| Step | May write | May run commands |
|---|---|---|
| Research, plan | The research notes or the plan only | Read-only |
| Plan review | Findings only | Read-only |
| Implement, repair | Its own checkout | Inside the checkout |
| Verify | A scratch folder and disposable test state | The service and its checks |

Commands the engine starts are wrapped so that writes outside the allowed folders
fail: `sandbox-exec` on macOS and bubblewrap on Linux. If the wrapper is not
available, the command does not run. Each executor's own permission settings are
set to match.

Hidden scenarios are stored outside the implementer's checkout, and the
implementer's steps are denied read access to them. See
[Verification](verification.md#hidden-scenarios).

## Guards against a stuck agent

| Guard | Trigger | Result |
|---|---|---|
| Repeated call | The same tool call with the same arguments, several times in a row | A reminder first; at the limit the step ends |
| No progress | The checkout is unchanged across two implementation rounds | The step ends |
| Phase cap | More rounds than the plan has phases, plus a margin | The step ends |
| Time limit | The step's time limit expires | The executor is stopped |

A step ended by a guard goes to Needs attention. It does not consume a repair.

Each implementation round ends with a structured report. "Complete" must list
evidence. "Blocked" must give a reason. The implementer's report never decides
that a work item is done; the checks and the verifier do.

## Skills

A skill is a folder with a `SKILL.md`. Its header gives a name and a one-line
description; the body is the instruction.

```text
skills/
├── research/   map-the-code, read-project-rules, recall-lessons
├── plan/       write-plan, split-into-phases, choose-checks, assess-risk
├── review/     review-plan, challenge-risk
├── implement/  implement-phase, follow-conventions, write-tests, self-check, checkpoint, flag-scope-change
├── verify/     verify-criteria, exercise-browser, replay-traffic, security-review, review-diff, write-findings
├── repair/     diagnose-failure, repair-in-scope
└── ready/      summarize-evidence, capture-lessons
```

The workflow names the skills for each step and the engine hands them to the
agent when the step starts. A service can add or replace skills in its own
repository, for example how to replay its traffic. A service skill with the same
name replaces the shared one. Skill versions are recorded in the run log.

## Package layout

```text
service_line/
├── cli.py                  # serve, add-service, new-item, approve, status, resume
├── server.py               # local web server for the UI
├── store/
│   ├── events.py           # the run log: append, replay, fold
│   ├── atomic.py           # durable writes and the run lock
│   ├── instances.py
│   └── workitems.py
├── engine/
│   ├── asl.py              # reads a workflow definition
│   ├── validate.py         # rejects a workflow that can skip approval or loop forever
│   ├── runner.py           # steps a run, brackets events, recovers after a crash
│   └── actions/            # research, plan, review, approval, implement, checks, verify, evaluate, repair
├── executors/
│   ├── base.py             # start, stop, result
│   ├── claude.py
│   ├── codex.py
│   └── guards.py           # repeated call, no progress, time limit
├── workspace/
│   ├── base.py             # files and commands behind one interface
│   └── local.py            # git worktree and command confinement on this machine
├── policy/
│   ├── permissions.py      # limits per step
│   ├── risk.py
│   └── killswitch.py
├── verification/
│   ├── guide.py
│   └── evidence.py
├── queue.py
├── notify.py
└── skills/
```

The engine uses the Python standard library plus the Claude Agent SDK. State is
plain files. There is no database and no workflow server.

## Deliberately left out

- **Plugins.** One engine, one set of steps.
- **Compressed logs and versioned log files.** A version number in the log header
  and load-time upgrades are enough for one machine.
- **Agent-written orchestration.** An agent may fan out helpers inside a step.
  The workflow itself is a reviewed file.
- **Resuming an agent mid-step.** Closing and re-running from a checkpoint is
  simpler to reason about than reattaching to a half-finished conversation.

## Where these choices come from

- The run log, crash closers, sandbox wrapper, guards, skill format, and executor
  contract follow the open-source
  [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness), read at the
  source level in November 2026. Service Line adds a per-step time limit, a hard
  stop for stuck agents, and no-progress detection, which that harness does not have.
- Fixed engine steps beside agent steps, and a cap of two repairs, follow
  [Stripe's description of its coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents).
- Hidden scenarios follow StrongDM's software factory, as described by
  [Simon Willison](https://simonwillison.net/2026/Feb/7/software-factory).
