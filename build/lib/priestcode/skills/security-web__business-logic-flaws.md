---
name: Business logic flaws
description: Business logic flaws: find, exploit (authorized), and fix.
category: security/web
tags: [business-logic, web]
---
# Business logic flaws

## When to use
Abusing intended functionality in unintended ways.

## Checklist
- Map the workflow; test negative/zero/huge quantities, skipped steps, replayed actions.
- Look for price/discount manipulation, step-skipping, and state confusion.
- FIX: enforce invariants server-side at each step.

## Pitfalls
- Trusting client-driven workflow order.
- Scanners don't find these — think like an abuser.
