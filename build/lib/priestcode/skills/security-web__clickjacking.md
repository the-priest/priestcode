---
name: Clickjacking
description: Clickjacking: find, exploit (authorized), and fix.
category: security/web
tags: [clickjacking, web]
---
# Clickjacking

## When to use
A sensitive UI that can be framed by another site.

## Checklist
- Check for X-Frame-Options / CSP frame-ancestors; try framing the page.
- FIX: set `frame-ancestors 'none'` (or specific origins) and X-Frame-Options: DENY.

## Pitfalls
- Only X-Frame-Options without CSP misses some browsers.
- Framebusting JS is bypassable.
