---
name: Dependency & supply-chain audit
description: Audit third-party dependencies for known CVEs and supply-chain risk.
category: security/appsec
tags: [dependencies, sca, cve, supply-chain]
---
# Dependency & supply-chain audit

## When to use
Before release, or auditing an unfamiliar project.

## Checklist
- Run the ecosystem scanner: pip-audit, npm audit, osv-scanner, cargo audit.
- Triage by reachability and severity — not every CVE is exploitable in your usage.
- Pin and lock versions; verify integrity (hashes/lockfiles).
- Watch for typosquats, recently-changed maintainers, install scripts.

## Pitfalls
- `npm audit` severity ≠ your exploitability; check reachability.
- Transitive deps carry most of the risk.

## Example
osv-scanner -r .   ;   pip-audit   ;   npm audit --production
