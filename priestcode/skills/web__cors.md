---
name: CORS
description: Configure CORS to allow what's needed and nothing more.
category: web
tags: [cors, web]
---
# CORS

## When to use
Working with cors.

## Checklist
- Allow specific origins, methods, headers — not `*` with credentials.
- Understand preflight (OPTIONS); don't reflect arbitrary Origin.
- CORS is not authorization.

## Pitfalls
- Reflecting Origin with credentials = any site can call your API.
- Treating CORS as a security boundary.
