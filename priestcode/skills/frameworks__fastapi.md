---
name: FastAPI
description: Build typed, validated FastAPI services.
category: frameworks
tags: [fastapi, python, async, backend]
---
# FastAPI

## When to use
Building an async Python API.

## Checklist
- Pydantic models for request/response validation; dependency injection for auth/db.
- Async endpoints for I/O; don't block the loop.
- Return explicit response models; document with the auto OpenAPI.

## Pitfalls
- Blocking calls in async endpoints stall the server.
- Leaking internal models as responses over-exposes data.
