---
name: C error handling
description: Handle errors correctly in C — the right mechanism, no swallowed failures.
category: languages/c
tags: [c, errors, exceptions]
---
# C error handling

## When to use
Any C code that can fail (I/O, parsing, network, external calls).

## Checklist
- Use the language's idiomatic error mechanism (exceptions or result types).
- Handle or propagate — never silently swallow; preserve context.
- Validate at boundaries and fail early with a clear message.

## Pitfalls
- Swallowing errors hides real failures.
- Generic catch-alls that lose the cause.
