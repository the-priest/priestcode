---
name: Python error handling
description: Handle errors correctly in Python — the right mechanism, no swallowed failures.
category: languages/python
tags: [python, errors, exceptions]
---
# Python error handling

## When to use
Any Python code that can fail (I/O, parsing, network, external calls).

## Checklist
- Catch the narrowest exception; never bare `except:`.
- Use `raise ... from e` to preserve the cause.
- Clean up with `with`/`finally`; don't swallow and continue silently.
- Validate at boundaries; fail loud early.

## Pitfalls
- Bare `except` hides bugs (incl. KeyboardInterrupt).
- Returning None on error forces callers to guess — raise or return a Result.
