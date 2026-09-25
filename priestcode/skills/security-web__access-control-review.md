---
name: Access control review
description: Systematically verify authorization across an app.
category: security/web
tags: [authz, access-control, owasp]
---
# Access control review

## When to use
Reviewing whether users can only do/see what they're allowed to.

## Checklist
- Map roles × resources × actions into a matrix; test each cell as each role.
- Vertical (user→admin) and horizontal (user A→user B) escalation.
- Force-browse admin URLs and hidden functions as a low-priv user.
- FIX: deny-by-default, centralized checks, enforce on the server for every action.

## Pitfalls
- UI hiding a button is not access control.
- Checks scattered per-endpoint get missed — centralize.
