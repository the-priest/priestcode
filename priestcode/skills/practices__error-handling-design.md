---
name: Error handling design
description: Design where and how failures are handled.
category: practices
tags: [errors, design]
---
# Error handling design

## When to use
Designing a module's failure behavior.

## Checklist
- Decide per error: recover, retry, or propagate — don't silently swallow.
- Fail fast at boundaries; keep the core assuming valid data.
- Preserve context up the stack; give the caller enough to act.

## Pitfalls
- Catch-all handlers that hide bugs.
- Returning sentinels that callers forget to check.
