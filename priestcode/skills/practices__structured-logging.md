---
name: Structured logging
description: Log so future-you can debug production.
category: practices
tags: [logging, observability]
---
# Structured logging

## When to use
Adding observability to a service.

## Checklist
- Structured (key=value/JSON) with levels; include a request/correlation id.
- Log decisions and boundaries, not noise; never log secrets/PII.
- Make errors actionable: what failed, with what inputs, and the cause.

## Pitfalls
- Logging secrets/PII is a breach.
- `print`-style logs without context are useless at 3am.
