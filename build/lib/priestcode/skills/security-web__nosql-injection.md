---
name: NoSQL injection
description: Find and fix NoSQL injection (MongoDB operator injection, etc.).
category: security/web
tags: [nosql, injection, mongodb]
---
# NoSQL injection

## When to use
Input reaching a NoSQL query, especially JSON bodies mapped straight into a query.

## Checklist
- Try operator injection: `{"$gt":""}`, `{"$ne":null}`, `{"$regex":"^a"}` in place of a value.
- Auth bypass: `{"user":{"$ne":null},"pass":{"$ne":null}}`.
- FIX: cast/validate types, reject objects where a scalar is expected, use an ODM with strict schemas.

## Pitfalls
- Passing a parsed JSON body straight into `find()` lets `$` operators through.
- Type juggling is the root — enforce that a password is a string.
