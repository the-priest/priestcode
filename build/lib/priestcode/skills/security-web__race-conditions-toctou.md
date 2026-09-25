---
name: Race conditions (TOCTOU)
description: Race conditions (TOCTOU): find, exploit (authorized), and fix.
category: security/web
tags: [race-condition, toctou, web]
---
# Race conditions (TOCTOU)

## When to use
A check and a use separated in time on shared state (balances, coupons, limits).

## Checklist
- Send many concurrent requests to the state-changing endpoint (e.g. redeem once → redeem many).
- Look for limit bypasses from parallelism.
- FIX: atomic operations / DB constraints / locks; enforce the invariant in one transaction.

## Pitfalls
- Application-level checks don't hold under concurrency.
- Idempotency keys and unique constraints are the fix, not more checks.
