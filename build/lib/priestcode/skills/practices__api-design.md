---
name: API design
description: Design an interface others can use without reading the source.
category: practices
tags: [api-design, interfaces]
---
# API design

## When to use
Designing a public function/class/endpoint.

## Checklist
- Make the common case easy and the API hard to misuse; consistent naming.
- Small surface; clear errors; document the contract and invariants.
- Version and keep backward compatibility for public APIs.

## Pitfalls
- Leaking implementation details in the interface.
- Breaking changes without versioning.
