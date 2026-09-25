---
name: Kotlin common pitfalls
description: The sharp edges of Kotlin that actually cause bugs — avoid them.
category: languages/kotlin
tags: [kotlin, pitfalls, footguns]
---
# Kotlin common pitfalls

## When to use
Writing or reviewing Kotlin; catching the language-specific bugs.

## Checklist
- Watch for: Platform types from Java can be null despite non-null types.
- Watch for: `!!` force-unwrap crashes on null.
- Watch for: Capturing `var` in lambdas; coroutine scope/cancellation leaks.
- Watch for: Equality: `==` (structural) vs `===` (referential).

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
