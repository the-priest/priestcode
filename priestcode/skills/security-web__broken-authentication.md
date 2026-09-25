---
name: Broken authentication
description: Assess and harden authentication — login, sessions, password handling.
category: security/web
tags: [auth, session, password, owasp]
---
# Broken authentication

## When to use
Any login, session, password reset, or 'remember me' flow.

## Checklist
- Check password storage: bcrypt/argon2/scrypt with a salt — never MD5/SHA/plain.
- Session: httpOnly+Secure+SameSite cookies, rotation on login, server-side invalidation on logout.
- Rate-limit and lock out credential stuffing; add MFA for sensitive accounts.
- Password reset: single-use, expiring, unguessable tokens; no user enumeration in responses.
- FIX: use a vetted auth library; don't roll your own.

## Pitfalls
- Fast hashes (SHA-256) are wrong for passwords — use a slow KDF.
- JWT in localStorage is XSS-exfiltratable; prefer httpOnly cookies.
- 'User not found' vs 'wrong password' leaks valid usernames.
