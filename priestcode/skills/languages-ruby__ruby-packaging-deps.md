---
name: Ruby packaging & deps
description: Structure, build, and ship a Ruby project and its dependencies.
category: languages/ruby
tags: [ruby, packaging, build, dependencies]
---
# Ruby packaging & deps

## When to use
Setting up, building, or releasing a Ruby project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
