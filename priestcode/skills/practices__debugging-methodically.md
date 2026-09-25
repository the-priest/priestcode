---
name: Debugging methodically
description: Find root causes fast, without flailing.
category: practices
tags: [debugging, troubleshooting]
---
# Debugging methodically

## When to use
Something is broken and you don't know why.

## Checklist
- Reproduce reliably first; read the actual error/traceback.
- Form ONE hypothesis; bisect the space (git bisect, binary search, prints).
- Change one thing at a time; fix the root cause; add a regression test.

## Pitfalls
- Shotgun-changing many things hides which fix worked.
- Fixing the symptom, not the cause.
