---
name: git bisect
description: Find the commit that introduced a bug fast.
category: git
tags: [bisect, git, vcs]
---
# git bisect

## When to use
Using git bisect.

## Checklist
- `git bisect start`; mark good/bad; test each midpoint (or `run` a script).
- Binary-search the history to the exact bad commit.
- Reset when done; add a regression test.

## Pitfalls
- A flaky test misleads bisect.
- Forgetting `git bisect reset` afterward.
