---
name: Subdomain takeover
description: Subdomain takeover: find, exploit (authorized), and fix.
category: security/web
tags: [subdomain-takeover, recon, cloud]
---
# Subdomain takeover

## When to use
Dangling DNS records pointing at unclaimed services.

## Checklist
- Enumerate subdomains; find CNAMEs to third-party services that return 'not found'/unclaimed.
- Confirm you can claim the resource; report/fix by removing the dangling record.
- FIX: remove stale DNS; decommission DNS with the service.

## Pitfalls
- Dangling records to deprovisioned buckets/apps are claimable.
- Fixing the service but leaving the DNS record.
