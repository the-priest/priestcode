---
name: Static binary analysis
description: Static binary analysis: find, exploit (authorized), and fix.
category: security/reversing
tags: [reversing, binary]
---
# Static binary analysis

## When to use
Understanding an unknown binary (authorized).

## Checklist
- Triage: file type, strings, imports, packing; then disassemble (Ghidra/radare2).
- Map the control flow; name functions; find the interesting logic (crypto, network, checks).
- Extract the primitive you need (keys, protocol, algorithm).

## Pitfalls
- Packed/obfuscated binaries need unpacking first.
- Getting lost — anchor on strings/imports/syscalls.
