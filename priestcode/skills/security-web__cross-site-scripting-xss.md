---
name: Cross-site scripting (XSS)
description: Find and fix XSS — reflected, stored, and DOM — where input becomes executable markup.
category: security/web
tags: [xss, injection, web, owasp, csp]
---
# Cross-site scripting (XSS)

## When to use
Any input that is rendered back into HTML/JS/attribute/URL context without correct encoding.

## Checklist
- Classify the sink context: HTML body, attribute, JS string, URL, or CSS — each needs different encoding.
- Reflected: inject `<script>`, `"><svg onload=...>`, event handlers; watch what survives.
- Stored: plant a payload, find where it renders for another user.
- DOM: trace `location`/`innerHTML`/`eval`/`document.write` sinks in JS.
- FIX: contextual output encoding, a strict CSP, `textContent` not `innerHTML`, framework auto-escaping left ON.

## Pitfalls
- Blacklisting `<script>` is bypassable (`<img onerror>`, `<svg>`, event handlers, JS URIs).
- `innerHTML +=` and template literals into the DOM are classic DOM-XSS sinks.
- A CSP with `unsafe-inline` gives almost no protection.

## Example
# CSP that actually helps:
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
