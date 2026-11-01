---
layout: docs
title: Verification
section: verification
permalink: /docs/verification/
---

# Verification needs evidence

Each product owns a versioned `service-line-verification.md` in its repository
root. An approved plan pins that guide and adds checks for the requested change.

[Use the service template](../templates/service-line-verification.md) ·
[Read this prototype's guide](../service-line-verification.md)

## Three responsibilities

| Part | Responsibility |
|---|---|
| **Service guide** | Startup, reset, fixtures, commands, browser flows, replay targets, assertions, required observations. |
| **Verify skill and session** | Follow the guide, exercise the environment, review the diff and results, return criterion-level findings. |
| **Engine** | Capture artifacts, validate their provenance and completeness, enforce approval, choose the next state. |

The verify skill is shared instructions, not a separate primitive. Its version is
pinned with the run. The verifier uses the selected executor in a separate session
and does not edit the implementation it reviews.

## Exercise the service

**Browser:** click, type, submit, navigate, and reload. Assert visible behavior,
network responses, and durable state. Capture actions, screenshots, console events,
and relevant requests.

**Traffic replay:** declare whether responses are mocked in the browser or
sanitized requests run against a real isolated backend. Mocking establishes
frontend behavior; backend replay also checks server behavior and state changes.
Pin fixtures, reset state, preserve relevant ordering, and assert side-effect counts.

**Observe:** correlate requests with required server logs, traces, database changes,
and queue activity. The guide names the signals that matter and explains anything
not applicable. Missing required observations make the result inconclusive.

## Accept or repair

Evidence records the exact code snapshot, including uncommitted changes, plan and
guide versions, fixture and environment identities, tool results, and artifact hashes.
Every mandatory check and review must pass against that snapshot.

A repair invalidates the old evidence. Failed assertions route to bounded repair;
missing evidence stops progress. A completion message or screenshot alone cannot
establish a pass. The engine validates consistency; evidence quality and review
still matter.

The current static prototype has no backend or replay fixtures. Its actual guide
checks browser interactions and state isolation. Evidence displayed inside the
mock UI is illustrative.
