---
name: File I/O safely
description: Read/write files without corruption or leaks.
category: systems
tags: [file-io, systems]
---
# File I/O safely

## When to use
Working with file i/o safely.

## Checklist
- Use context managers; explicit encodings; handle missing/locked files.
- Atomic writes (temp + rename) for durability; avoid partial writes.
- Stream large files; clean up temp files.

## Pitfalls
- Non-atomic writes corrupt on crash.
- Leaking file handles; wrong/implicit encoding.
