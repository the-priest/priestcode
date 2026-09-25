---
name: HTTP request smuggling
description: HTTP request smuggling: find, exploit (authorized), and fix.
category: security/web
tags: [request-smuggling, web]
---
# HTTP request smuggling

## When to use
Front-end and back-end disagree on request boundaries.

## Checklist
- Probe CL.TE / TE.CL discrepancies carefully in an authorized lab.
- Detect via timing/differential responses; understand the proxy chain.
- FIX: normalize/reject ambiguous length headers; use HTTP/2 end-to-end.

## Pitfalls
- This can poison other users' requests — test only with authorization.
- Ambiguous Content-Length/Transfer-Encoding is the root.
