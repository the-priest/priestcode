---
name: Insecure direct object reference (IDOR)
description: Find and fix IDOR/broken object-level authorization — accessing others' objects by id.
category: security/web
tags: [idor, authz, bola, api, owasp]
---
# Insecure direct object reference (IDOR)

## When to use
Any endpoint that takes an object id (/orders/123) and returns/edits it.

## Checklist
- Enumerate ids as user A, then request them as user B — do you get A's data?
- Try sequential, UUID, and encoded ids; check every verb (GET/PUT/DELETE), not just GET.
- Check indirect refs: filenames, export ids, nested resources.
- FIX: authorize on EVERY request — scope the query to the current user (WHERE owner_id = me), don't trust the id alone.

## Pitfalls
- Authentication is not authorization — being logged in ≠ allowed to see object 123.
- Hiding the id (UUID) is not a fix; enforce ownership server-side.
- Mass-assignment often rides along — bind only allowed fields.
