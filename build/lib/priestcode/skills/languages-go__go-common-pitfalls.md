---
name: Go common pitfalls
description: The sharp edges of Go that actually cause bugs — avoid them.
category: languages/go
tags: [go, pitfalls, footguns]
---
# Go common pitfalls

## When to use
Writing or reviewing Go; catching the language-specific bugs.

## Checklist
- Watch for: `nil` interface != nil concrete; the typed-nil gotcha.
- Watch for: Loop variable captured by goroutines (pre-1.22) shares one var.
- Watch for: Ignoring returned errors; unchecked type assertions panic.
- Watch for: Slices share backing arrays — append can mutate aliases.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
