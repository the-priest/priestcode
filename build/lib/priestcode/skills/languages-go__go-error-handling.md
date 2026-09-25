---
name: Go error handling
description: Handle errors correctly in Go — the right mechanism, no swallowed failures.
category: languages/go
tags: [go, errors, exceptions]
---
# Go error handling

## When to use
Any Go code that can fail (I/O, parsing, network, external calls).

## Checklist
- Use the language's idiomatic error mechanism (exceptions or result types).
- Handle or propagate — never silently swallow; preserve context.
- Validate at boundaries and fail early with a clear message.

## Pitfalls
- Swallowing errors hides real failures.
- Generic catch-alls that lose the cause.
