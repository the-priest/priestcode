---
name: Subprocess handling
description: Run child processes safely and robustly.
category: systems
tags: [subprocess, systems]
---
# Subprocess handling

## When to use
Working with subprocess handling.

## Checklist
- Pass argv arrays, never shell strings with input; set timeouts.
- Capture stdout/stderr; check return codes; kill on timeout (and the process group).
- Stream output for long runs; avoid deadlocks on full pipes.

## Pitfalls
- shell=True with input = command injection.
- Not reading pipes → child blocks on a full buffer.
