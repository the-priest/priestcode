---
name: Git recovery
description: Recover from git mistakes safely.
category: practices
tags: [git, recovery]
---
# Git recovery

## When to use
You committed/reset/rebased wrong and need to fix it.

## Checklist
- `git reflog` finds 'lost' commits; reset/cherry-pick back to them.
- Undo a bad commit with `git revert` (shared) or `reset` (local only).
- Recover deleted branches from reflog; stash rescues uncommitted work.
- Prefer non-destructive fixes on shared history.

## Pitfalls
- `reset --hard` / force-push on shared branches destroys others' work.
- `push --force` over `--force-with-lease` clobbers teammates.
