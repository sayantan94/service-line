---
name: checkpoint
description: Use at the end of every phase and repair, so the engine can commit a clean, working state to return to.
---

# Checkpoint

Leave the checkout in a state the engine can safely commit and, if needed later, safely reset to.

## Do

1. Finish or undo any half-made edit. Nothing should be left mid-change.
2. Make sure the code builds or imports and the quick checks run.
3. Remove temporary files, scratch scripts and debugging output you created.
4. Do not run `git commit`, `git stash`, `git reset` or change branches. The engine owns the history.
5. Say in your final message what state you are leaving: what is done, and what the next phase starts from.

## Good output

- The working tree holds only intended changes.
- The next phase, or a retry after a crash, can start from this point without knowing what you were thinking.
- Your final message is enough for someone to pick up the work.

## Avoid

- Committing, amending or rewriting history yourself.
- Leaving generated files, caches or logs for the engine to commit.
- Leaving a note to yourself in a file instead of in your final message.
- Relying on anything outside the checkout, such as a file in your home folder, to carry state.
