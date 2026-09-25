---
name: Rust packaging & deps
description: Structure, build, and ship a Rust project and its dependencies.
category: languages/rust
tags: [rust, packaging, build, dependencies]
---
# Rust packaging & deps

## When to use
Setting up, building, or releasing a Rust project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
