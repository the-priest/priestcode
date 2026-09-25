---
name: Forms & validation
description: Build forms that validate and fail gracefully.
category: web
tags: [forms, web]
---
# Forms & validation

## When to use
Working on forms & validation.

## Checklist
- Validate on the client for UX AND on the server for safety; clear inline errors.
- Accessible labels/errors; preserve input on failure; protect against CSRF.
- Debounce async validation.

## Pitfalls
- Client-only validation is bypassable.
- Losing the user's input on a failed submit.
