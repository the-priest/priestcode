---
name: Django
description: Build secure, idiomatic Django apps.
category: frameworks
tags: [django, python, backend]
---
# Django

## When to use
Building or reviewing a Django project.

## Checklist
- Use the ORM with parameterized queries; migrations for schema.
- Keep views thin, logic in models/services; use forms/serializers for validation.
- CSRF middleware on; never disable it for convenience; use `select_related`/`prefetch_related`.
- Secrets in env; DEBUG=False in prod; ALLOWED_HOSTS set.

## Pitfalls
- `.raw()`/`.extra()` reintroduce SQLi.
- N+1 queries from lazy relations.
- DEBUG=True in prod leaks everything.
