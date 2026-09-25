---
name: SQL injection
description: Find and exploit (or fix) SQL injection — string-built queries that let input change the query.
category: security/web
tags: [sqli, injection, web, database, owasp]
---
# SQL injection

## When to use
Any place user input reaches a SQL query as text rather than a bound parameter.

## Checklist
- Map every sink: string-concatenated or f-string SQL, ORM `.raw()`/`.extra()`, dynamic ORDER BY.
- Probe with a single quote, then `' OR '1'='1`, then boolean/time-based payloads (`' AND SLEEP(5)--`).
- Confirm with a differential: true vs false condition changes the response.
- Escalate: UNION SELECT to read columns, then schema (information_schema), then data.
- For blind: boolean or time-based extraction, one char at a time (or sqlmap).
- FIX: parameterized queries / prepared statements ONLY; never format SQL with input; least-priv DB user.

## Pitfalls
- `ORDER BY` and identifiers can't be parameterized — allow-list them, don't concatenate.
- ORMs are not immune: `.raw()`, `.extra()`, and `.filter(RawSQL(...))` reintroduce it.
- Escaping quotes is not a fix; parameterization is.

## Example
sqlmap -u 'https://t/item?id=1' --batch --dbs   # authorized targets only
# fix (python): cur.execute('SELECT * FROM u WHERE id=%s', (uid,))
