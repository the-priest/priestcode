---
name: Memory leak hunting
description: Track down growing memory use.
category: performance
tags: [memory-leaks, performance]
---
# Memory leak hunting

## When to use
Working on memory leak hunting.

## Checklist
- Confirm growth over time; snapshot/diff the heap; find retained references.
- Common causes: unbounded caches/lists, listeners not removed, closures capturing.
- Fix and verify the curve flattens.

## Pitfalls
- Unbounded caches masquerading as leaks.
- Event listeners/subscriptions never removed.
