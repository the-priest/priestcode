---
name: GraphQL
description: Design schemas and resolvers that are safe and performant.
category: web
tags: [graphql, web]
---
# GraphQL

## When to use
Working with graphql.

## Checklist
- Design the schema around client needs; resolve without N+1 (dataloaders).
- Limit query depth/complexity; authorize per field.
- Disable introspection in prod if sensitive.

## Pitfalls
- Unbounded nested queries = DoS.
- Missing field-level authz.
