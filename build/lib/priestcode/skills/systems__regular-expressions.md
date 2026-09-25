---
name: Regular expressions
description: Write correct, safe regexes.
category: systems
tags: [regex, systems]
---
# Regular expressions

## When to use
Working with regular expressions.

## Checklist
- Anchor and be specific; prefer explicit character classes; test against edge cases.
- Watch catastrophic backtracking (nested quantifiers); use non-greedy carefully.
- For structured formats, prefer a real parser over a mega-regex.

## Pitfalls
- ReDoS from `(a+)+`-style patterns on hostile input.
- Parsing HTML/recursive formats with regex.
