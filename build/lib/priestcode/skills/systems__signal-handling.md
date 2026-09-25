---
name: Signal handling
description: Handle process signals for clean shutdown.
category: systems
tags: [signals, systems]
---
# Signal handling

## When to use
Working with signal handling.

## Checklist
- Trap SIGTERM/SIGINT; flush and clean up; exit promptly.
- Make handlers minimal and reentrancy-safe; propagate to children.
- Support graceful drain before exit.

## Pitfalls
- Ignoring SIGTERM → hard kills lose in-flight work.
- Heavy work inside a signal handler.
