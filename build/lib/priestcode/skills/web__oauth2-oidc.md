---
name: OAuth2 & OIDC
description: Integrate OAuth2/OpenID Connect correctly.
category: web
tags: [oauth, web]
---
# OAuth2 & OIDC

## When to use
Working with oauth2 & oidc.

## Checklist
- Use auth code flow + PKCE for apps; validate state; verify tokens (sig/aud/exp/iss).
- Store tokens safely; refresh correctly; scope minimally.
- Never put secrets in a public client.

## Pitfalls
- Implicit flow / tokens in URLs leak.
- Skipping token validation.
