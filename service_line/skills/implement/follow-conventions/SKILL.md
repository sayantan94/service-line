---
name: follow-conventions
description: Use whenever editing code, so the change reads as if the repository's own authors wrote it.
---

# Follow conventions

Keep the codebase consistent, so the change is easy to review and maintain.

## Do

1. Before writing, read two or three nearby examples of the same kind of thing: a function, a test, a handler.
2. Match their naming, file layout, error handling, logging and comment style.
3. Use the helpers and patterns the repository already has before adding new ones.
4. Keep imports, formatting and line length the way the surrounding file has them.
5. Follow any rules recorded during research, such as required headers or forbidden dependencies.
6. If a convention seems wrong, follow it anyway and mention it in your final message.

## Good output

- A reviewer cannot tell from style alone which lines are new.
- No new dependency, pattern or abstraction unless the plan called for it.
- New tests look like the existing tests beside them.

## Avoid

- Reformatting or renaming code you are not otherwise changing. It buries the real change in the diff.
- Bringing in a preferred library or idiom from elsewhere.
- Adding comments that narrate what the code does line by line.
- Leaving debugging output, commented-out code or unused helpers behind.
