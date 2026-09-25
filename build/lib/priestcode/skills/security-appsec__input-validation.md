---
name: Input validation
description: Input validation: find, exploit (authorized), and fix.
category: security/appsec
tags: [validation, appsec]
---
# Input validation

## When to use
Any boundary receiving external data.

## Checklist
- Validate type, range, length, and format at the trust boundary; allow-list where possible.
- Reject rather than sanitize when you can; canonicalize before checks.
- Validate on the server even if the client does too.

## Pitfalls
- Client-side validation is a UX feature, not a security control.
- Blocklists miss cases allow-lists wouldn't.
