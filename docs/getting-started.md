---
layout: docs
title: Try the prototype
section: start
permalink: /docs/getting-started/
---

# Try the prototype

[Open the mock UI](../service-line-ui.html). You can also clone the repository and
open `service-line-ui.html` directly. No installation or credentials are needed.

## Follow a work item

1. Select **AppliedIn** from Services or the top switcher.
2. Open **WI-042** in the Approval stage. Read the plan and required checks.
3. Keep **Failed check → repair** selected and approve the plan.
4. Use **Next sample step** to follow the failure, repair, fresh checks, and review.
5. Inspect the evidence and candidate lesson. Switch services to check isolation.

Use **Missing evidence** to see a blocked run. Request a plan change to exercise
renewed approval and explicit human acceptance. **Reset** restores all examples.

## Add a service

Enter a repository path, then select **Read repository with Claude**. The intended
runtime reads the README, project instructions, and test configuration to draft
the description and test command. Both remain editable. Reading does not execute
the proposed command. Select the default executor for subsequent work separately.

The prototype supplies a bundled AppliedIn example for paths ending in `AppliedIn`.
It does not inspect arbitrary folders or invoke Claude. Unknown repositories need
manual fields in this preview.

## Current scope

| Available | Proposed runtime work |
|---|---|
| Service picker and factory line | Filesystem instances and isolated checkouts |
| Editable plans and simulated approval gates | Durable approval records and resumable state |
| Session and lesson views | Codex and Claude adapters with persistent sessions |
| Illustrative checks and evidence | Commands, browser execution, backend replay, artifact capture |

All mock state stays in the page and resets on reload. No merges, deployments,
external submissions, or real test runs occur from its controls.
