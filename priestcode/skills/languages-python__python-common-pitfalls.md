---
name: Python common pitfalls
description: The sharp edges of Python that actually cause bugs — avoid them.
category: languages/python
tags: [python, pitfalls, footguns]
---
# Python common pitfalls

## When to use
Writing or reviewing Python; catching the language-specific bugs.

## Checklist
- Watch for: Mutable default arguments persist across calls.
- Watch for: Late-binding closures in loops capture the variable, not its value.
- Watch for: `is` vs `==`; integer/​string identity caching is not guaranteed.
- Watch for: Bare `except` swallows KeyboardInterrupt/SystemExit.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
