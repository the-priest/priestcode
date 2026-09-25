---
name: Cherry-pick & revert
description: Move or undo specific commits safely.
category: git
tags: [cherry-pick, git, vcs]
---
# Cherry-pick & revert

## When to use
Using cherry-pick & revert.

## Checklist
- Cherry-pick to port a fix to another branch; revert to undo on shared history.
- Resolve conflicts carefully; keep the intent.
- Prefer revert over reset on anything pushed.

## Pitfalls
- Reset --hard on shared branches loses work.
- Cherry-picking creating duplicate commits/conflicts on later merge.
