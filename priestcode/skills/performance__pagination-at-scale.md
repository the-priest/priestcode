---
name: Pagination at scale
description: Page large result sets efficiently.
category: performance
tags: [pagination, performance]
---
# Pagination at scale

## When to use
Working on pagination at scale.

## Checklist
- Prefer keyset/cursor pagination over OFFSET for large tables.
- Index the sort key; return a stable cursor; cap page size.
- Avoid COUNT(*) on huge tables per page.

## Pitfalls
- OFFSET pagination degrades linearly on deep pages.
- Unstable ordering skips/repeats rows.
