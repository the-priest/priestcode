---
name: Server-side request forgery (SSRF)
description: Find and fix SSRF — making the server issue attacker-controlled requests.
category: security/web
tags: [ssrf, web, cloud, owasp]
---
# Server-side request forgery (SSRF)

## When to use
Any feature that fetches a URL the user supplies (webhooks, image/URL preview, imports, PDF render).

## Checklist
- Point the fetch at `http://169.254.169.254/` (cloud metadata), `http://localhost`, internal IPs.
- Try alternate encodings: decimal/octal IPs, `[::1]`, `0.0.0.0`, DNS rebinding, redirects to internal.
- Check what comes back (blind SSRF still leaks via timing/errors/OOB).
- FIX: allow-list destinations, resolve then validate the IP (block private/link-local), disable redirects, drop unused URL schemes.

## Pitfalls
- Blocking `localhost` by string is bypassable — resolve the host and check the IP.
- Redirects re-introduce SSRF; validate the FINAL IP, not just the first.
- Fail CLOSED when the host can't be resolved/validated — never fall through to the request.

## Example
# fix: resolve, reject private ranges (ipaddress.ip_address(ip).is_private), no redirects
