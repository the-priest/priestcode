---
name: Open redirect
description: Open redirect: find, exploit (authorized), and fix.
category: security/web
tags: [open-redirect, web]
---
# Open redirect

## When to use
A redirect target taken from user input (?next=, ?url=).

## Checklist
- Supply an external URL and see if the app redirects off-site.
- Try `//evil.com`, `https:evil.com`, and encoded variants.
- FIX: allow-list redirect targets or only permit relative paths.

## Pitfalls
- `//host` is protocol-relative and escapes naive checks.
- Open redirects enable phishing and OAuth token theft.
