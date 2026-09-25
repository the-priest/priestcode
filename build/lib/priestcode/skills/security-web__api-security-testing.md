---
name: API security testing
description: Test a REST/GraphQL API for the API-specific top risks.
category: security/web
tags: [api, rest, graphql, authz]
---
# API security testing

## When to use
Any API assessment.

## Checklist
- BOLA/IDOR on every object id; function-level authz on every verb and admin route.
- Mass assignment: send extra fields (role, is_admin) and see if they bind.
- Rate limiting, resource exhaustion, and excessive data exposure in responses.
- GraphQL: introspection, query depth/complexity, batching abuse, field-level authz.
- FIX: authorize server-side per object+action; return only needed fields; cap depth/rate.

## Pitfalls
- Client-side field hiding ≠ authorization.
- GraphQL introspection + deep queries enable enumeration and DoS.
