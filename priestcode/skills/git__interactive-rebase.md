---
name: Interactive rebase
description: Clean up history with interactive rebase.
category: git
tags: [rebase, git, vcs]
---
# Interactive rebase

## When to use
Using interactive rebase.

## Checklist
- `git rebase -i` to squash/reorder/edit/drop commits before sharing.
- Rewrite messages; split commits; keep each commit buildable.
- Only rewrite UNPUSHED/local history.

## Pitfalls
- Rebasing shared branches rewrites others' history.
- Force-push clobbering teammates (use --force-with-lease).
