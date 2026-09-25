---
name: React components & state
description: Build correct React components with clean state and effects.
category: frameworks
tags: [react, frontend, hooks]
---
# React components & state

## When to use
Building or fixing a React UI.

## Checklist
- Keep components small and pure; lift state only as high as needed.
- Effects for synchronization only; list every dependency; clean up subscriptions.
- Key lists by stable ids, never index; memoize only measured hot renders.
- Derive state, don't duplicate it.

## Pitfalls
- Missing effect deps cause stale closures.
- Index keys corrupt lists on reorder.
- Overusing useMemo/useCallback adds noise and bugs.
