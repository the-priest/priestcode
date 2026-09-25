---
name: Path traversal
description: Path traversal: find, exploit (authorized), and fix.
category: security/web
tags: [path-traversal, lfi, web]
---
# Path traversal

## When to use
A file path built from user input.

## Checklist
- Try `../` sequences (and encoded `%2e%2e%2f`, double-encoding) to escape the intended dir.
- Reach sensitive files (/etc/passwd, app config, source).
- FIX: resolve the path and confirm it stays under the allowed root; allow-list names; never concatenate raw input.

## Pitfalls
- Blacklisting `../` misses encodings; canonicalize then check the prefix.
- Symlinks can escape a naive prefix check.
