---
name: Express (Node)
description: Build secure Express APIs.
category: frameworks
tags: [express, node, backend]
---
# Express (Node)

## When to use
Building a Node/Express service.

## Checklist
- Validate input (zod/joi); use helmet; parameterize queries.
- Centralized error middleware; async handlers wrapped to catch rejections.
- Rate-limit and set CORS deliberately.

## Pitfalls
- Unhandled promise rejections crash the process.
- Trusting req.body shape leads to mass-assignment.
