---
name: Rails
description: Build idiomatic Rails apps with its conventions and security defaults.
category: frameworks
tags: [rails, framework]
---
# Rails

## When to use
Building or reviewing a Rails project.

## Checklist
- Follow Rails's project structure and conventions.
- Validate all input; keep secrets in env; parameterize data access.
- Use the framework's auth/session/CSRF features rather than rolling your own.
- Write tests with the framework's standard tooling.

## Pitfalls
- Fighting the framework's conventions creates unmaintainable code.
- Disabling built-in security features for convenience.
