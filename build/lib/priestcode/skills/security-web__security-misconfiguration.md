---
name: Security misconfiguration
description: Find misconfigurations — debug endpoints, default creds, verbose errors, open buckets.
category: security/web
tags: [misconfig, hardening, owasp]
---
# Security misconfiguration

## When to use
Deployment review, or when a target exposes more than it should.

## Checklist
- Look for debug mode on in prod, stack traces, exposed /admin, actuator, .git, .env, backups.
- Check default/weak credentials on every service.
- Check security headers (HSTS, CSP, X-Content-Type-Options), directory listing, open cloud storage.
- FIX: harden defaults, disable debug, strip banners, close/authenticate management endpoints.

## Pitfalls
- `.git/` and `.env` served statically leak the whole app.
- Verbose errors are a recon goldmine.
