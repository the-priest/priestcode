---
name: Cross-platform code
description: Write code that works across OSes.
category: systems
tags: [cross-platform, portability]
---
# Cross-platform code

## When to use
Code that must run on Linux/macOS/Windows.

## Checklist
- Use the stdlib path/OS abstractions (pathlib/os.path); avoid shelling out to OS-specific tools.
- Handle path separators, line endings, and case sensitivity; detect the platform when needed.
- Test on each target (CI matrix).

## Pitfalls
- Hardcoded `/` paths or platform-specific commands.
- Assuming a case-sensitive/insensitive filesystem.
