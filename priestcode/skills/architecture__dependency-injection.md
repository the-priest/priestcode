---
name: Dependency injection
description: Invert dependencies for testability.
category: architecture
tags: [dependency-injection, architecture]
---
# Dependency injection

## When to use
Deciding on dependency injection.

## Checklist
- Pass collaborators in (constructor/args) rather than constructing them inside.
- Depend on interfaces; wire concrete types at the edge (composition root).
- This makes units testable with fakes.

## Pitfalls
- A heavyweight DI framework where plain params suffice.
- Hidden global singletons defeating the point.
