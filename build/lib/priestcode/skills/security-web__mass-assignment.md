---
name: Mass assignment
description: Mass assignment: find, exploit (authorized), and fix.
category: security/web
tags: [mass-assignment, web, api]
---
# Mass assignment

## When to use
An endpoint binding request fields straight onto a model.

## Checklist
- Send extra fields (role, is_admin, verified) and see if they persist.
- FIX: bind an explicit allow-list of fields; never trust the whole body.

## Pitfalls
- Auto-binding the request body onto the model object.
- Hidden fields aren't protection.
