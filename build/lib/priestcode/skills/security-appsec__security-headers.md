---
name: Security headers
description: Set the HTTP security headers that matter.
category: security/appsec
tags: [headers, hardening, web]
---
# Security headers

## When to use
Hardening any web response.

## Checklist
- CSP (no unsafe-inline), HSTS, X-Content-Type-Options: nosniff, frame-ancestors, Referrer-Policy.
- Set them globally at the edge/middleware; test with a header scanner.
- Tune CSP to the app; report-only first, then enforce.

## Pitfalls
- A CSP with unsafe-inline gives little protection.
- Setting headers on some routes but not others.
