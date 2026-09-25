---
name: git submodules & subtrees
description: Manage nested repos correctly.
category: git
tags: [submodules, git, vcs]
---
# git submodules & subtrees

## When to use
Using git submodules & subtrees.

## Checklist
- Understand submodule pinning (a commit, not a branch); update deliberately.
- Clone with `--recursive`; document the workflow; consider subtree as an alternative.
- Keep the pointer commit in sync.

## Pitfalls
- Forgetting to init/update submodules → empty dirs.
- Detached-HEAD confusion inside submodules.
