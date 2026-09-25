---
name: Incident response basics
description: Incident response basics: find, exploit (authorized), and fix.
category: security/blue
tags: [dfir, incident-response, blue-team]
---
# Incident response basics

## When to use
Responding to a suspected compromise.

## Checklist
- Contain first (isolate), preserve evidence (don't wipe), then investigate.
- Build a timeline from logs; scope the blast radius; identify entry + persistence.
- Eradicate, recover, and write the postmortem with concrete fixes.

## Pitfalls
- Rebooting/reimaging destroys volatile evidence.
- Declaring 'clean' without finding the entry point.
