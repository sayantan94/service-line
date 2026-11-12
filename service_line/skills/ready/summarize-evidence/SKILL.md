---
name: summarize-evidence
description: Use when a work item reaches Ready, to tell the person reviewing it what changed and how it was verified.
---

# Summarize evidence

Let a person decide whether to merge in a few minutes, without rereading the whole run.

## Do

1. Say what changed in two or three plain sentences, naming the files.
2. List each acceptance criterion with the check that proved it and its result.
3. State what the verifier did and found, including hidden scenarios.
4. State how many repairs were needed and what they fixed.
5. Name anything not verified, and anything the reviewer should look at closely given the risk level.
6. Give the revision the evidence belongs to.

## Good output

- A reviewer can see what to look at first.
- Nothing is described as verified that was not.
- Plain words, no internal step names.

## Avoid

- Describing the work as done or shipped. Ready means ready for review; merging is the person's decision.
- Leaving out a repair or a finding because the final result passed.
- Restating the plan instead of what was actually built.
- Long narrative. The reviewer wants the result and where to look.
