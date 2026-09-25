---
name: REST API design
description: Consistent resources, correct status codes, versioning, pagination, clear errors.
category: web
tags: [rest, web]
---
# REST API design

## When to use
Working with rest api design.

## Checklist
- Model resources (nouns) with proper verbs and status codes.
- Paginate lists; version the API; return consistent error shapes.
- Idempotent PUT/DELETE; validate and authorize every request.

## Pitfalls
- Verbs in URLs and 200-for-everything.
- Unbounded list endpoints.
