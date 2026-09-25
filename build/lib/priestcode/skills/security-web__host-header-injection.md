---
name: Host header injection
description: Host header injection: find, exploit (authorized), and fix.
category: security/web
tags: [host-header, web]
---
# Host header injection

## When to use
The app trusts the Host header for links/logic.

## Checklist
- Change Host/X-Forwarded-Host; check password-reset links, redirects, cache keys.
- FIX: use a configured canonical host; validate/allow-list Host; don't build links from it.

## Pitfalls
- Password-reset poisoning via attacker-controlled Host.
- Trusting X-Forwarded-* without a trusted proxy.
