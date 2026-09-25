---
name: JavaScript error handling
description: Handle errors correctly in JavaScript — the right mechanism, no swallowed failures.
category: languages/javascript
tags: [javascript, errors, exceptions]
---
# JavaScript error handling

## When to use
Any JavaScript code that can fail (I/O, parsing, network, external calls).

## Checklist
- try/catch around async awaits; reject with Error objects, not strings.
- Handle promise rejections; add a global unhandledRejection handler.
- Validate inputs at the edge.

## Pitfalls
- Unhandled promise rejections crash or silently drop.
- Throwing non-Error loses the stack.
