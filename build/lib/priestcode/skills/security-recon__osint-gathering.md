---
name: OSINT gathering
description: Collect open-source intelligence on a target org (authorized).
category: security/recon
tags: [osint, recon, footprinting]
---
# OSINT gathering

## When to use
Pre-engagement footprinting within an authorized scope.

## Checklist
- Domains/subdomains (crt.sh, amass), IP ranges, ASN.
- Employees, emails, tech stack (LinkedIn, job posts, BuiltWith).
- Leaked creds (HIBP), exposed docs, code (GitHub dorking for secrets).
- Cloud assets, S3 buckets, exposed dashboards.

## Pitfalls
- Stay within scope and legality — passive doesn't mean unlimited.
- GitHub secret leaks are common — search org repos and forks.
