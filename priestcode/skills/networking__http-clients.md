---
name: HTTP clients
description: Make robust outbound HTTP calls.
category: networking
tags: [http-client, networking]
---
# HTTP clients

## When to use
Working with http clients.

## Checklist
- Set connect+read timeouts; retry idempotent calls with backoff+jitter.
- Handle non-2xx explicitly; stream large bodies; reuse connections.
- Validate/limit redirects (SSRF).

## Pitfalls
- No timeout → the call hangs your service.
- Retrying non-idempotent calls duplicates side effects.
