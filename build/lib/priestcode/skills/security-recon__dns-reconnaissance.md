---
name: DNS reconnaissance
description: DNS reconnaissance: find, exploit (authorized), and fix.
category: security/recon
tags: [dns, recon]
---
# DNS reconnaissance

## When to use
Mapping a target's DNS footprint (authorized).

## Checklist
- Enumerate records (A/AAAA/MX/TXT/NS/CNAME); brute subdomains; check zone transfer (AXFR).
- Use cert transparency (crt.sh) and passive DNS for more names.
- Map the results into the attack surface.

## Pitfalls
- Zone transfer is rarely open but a jackpot when it is.
- Wildcard DNS causes false-positive subdomains.
