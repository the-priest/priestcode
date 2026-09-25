---
name: Transactions & isolation
description: Use DB transactions and isolation levels correctly.
category: databases
tags: [transactions, acid, database]
---
# Transactions & isolation

## When to use
Multi-step writes that must be consistent.

## Checklist
- Wrap related writes in one transaction; keep them short.
- Pick isolation for the anomaly you must prevent (lost update, phantom).
- Handle serialization failures with retries; avoid holding locks over network calls.

## Pitfalls
- Long transactions block others and bloat MVCC.
- Assuming default isolation prevents all anomalies.
