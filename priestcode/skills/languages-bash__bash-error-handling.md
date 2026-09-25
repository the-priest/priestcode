---
name: Bash error handling
description: Handle errors correctly in Bash — the right mechanism, no swallowed failures.
category: languages/bash
tags: [bash, errors, exceptions]
---
# Bash error handling

## When to use
Any Bash code that can fail (I/O, parsing, network, external calls).

## Checklist
- Use the language's idiomatic error mechanism (exceptions or result types).
- Handle or propagate — never silently swallow; preserve context.
- Validate at boundaries and fail early with a clear message.

## Pitfalls
- Swallowing errors hides real failures.
- Generic catch-alls that lose the cause.
