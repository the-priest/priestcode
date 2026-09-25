---
name: Microservices vs monolith
description: Choose and structure service boundaries.
category: architecture
tags: [microservices, architecture]
---
# Microservices vs monolith

## When to use
Deciding on microservices vs monolith.

## Checklist
- Start with a well-structured monolith; split only for real scaling/team boundaries.
- Services own their data; communicate via clear contracts; design for partial failure.
- Weigh the operational cost of distribution.

## Pitfalls
- Premature microservices multiply complexity.
- Shared databases coupling 'independent' services.
