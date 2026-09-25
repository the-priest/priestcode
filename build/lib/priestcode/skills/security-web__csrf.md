---
name: CSRF
description: Find and fix cross-site request forgery — state-changing requests without an anti-forgery token.
category: security/web
tags: [csrf, web, cookies, owasp]
---
# CSRF

## When to use
Any cookie-authenticated, state-changing endpoint (POST/PUT/DELETE).

## Checklist
- Check for an anti-CSRF token that is validated server-side and bound to the session.
- Check SameSite on the session cookie (Lax/Strict blocks most cross-site sends).
- FIX: per-session CSRF tokens on all mutating requests + SameSite cookies; don't rely on referer alone.

## Pitfalls
- GET requests that change state are CSRF-able and cache-poisonable.
- CORS is not CSRF protection.
- SameSite=None without a token re-opens it.
