---
name: JavaScript performance
description: Profile and speed up JavaScript code with evidence.
category: languages/javascript
tags: [javascript, performance]
---
# JavaScript performance

## When to use
A JavaScript hot path that's too slow — measured, not guessed.

## Checklist
- Profile in DevTools; avoid layout thrash; debounce/throttle events.
- Minimize main-thread work; lazy-load; memoize pure work.
- Measure with real traces.

## Pitfalls
- Premature memoization adds bugs.
- Big synchronous JSON parses block the loop.
