---
name: JWT attacks
description: Assess and fix JSON Web Token handling — alg confusion, weak secrets, missing checks.
category: security/web
tags: [jwt, auth, crypto]
---
# JWT attacks

## When to use
Any system using JWTs for auth/session.

## Checklist
- Check `alg`: reject `none`; don't let RS256↔HS256 confusion use the public key as an HMAC secret.
- Crack weak HMAC secrets offline (hashcat mode 16500).
- Verify exp/nbf/aud/iss are actually checked; check for missing signature verification.
- FIX: pin the algorithm, strong secret or proper key, verify all claims, short expiry + rotation.

## Pitfalls
- `alg:none` and alg-confusion come from libraries that trust the header's alg.
- JWTs can't be revoked without extra state — plan for logout/rotation.

## Example
hashcat -m 16500 jwt.txt wordlist.txt   # authorized testing
