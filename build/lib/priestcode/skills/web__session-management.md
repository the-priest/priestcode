---
name: Session management
description: Manage web sessions securely.
category: web
tags: [session, auth, web]
---
# Session management

## When to use
Any stateful, authenticated web app.

## Checklist
- Server-side sessions or signed tokens; httpOnly+Secure+SameSite cookies.
- Rotate the id on login/privilege change; expire idle + absolute; invalidate on logout.
- Bind minimal data; protect against fixation and CSRF.

## Pitfalls
- Session fixation from not rotating the id at login.
- Long-lived sessions with no server-side invalidation.
