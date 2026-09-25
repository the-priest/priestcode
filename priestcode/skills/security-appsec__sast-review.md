---
name: SAST review
description: SAST review: find, exploit (authorized), and fix.
category: security/appsec
tags: [sast, static-analysis, appsec]
---
# SAST review

## When to use
Static review of a codebase for vulns.

## Checklist
- Run semgrep/bandit with security rulesets; triage by reachability.
- Manually audit auth, input handling, crypto, and dangerous sinks the scanner flags.
- Confirm each finding in context; drop false positives; fix real ones.

## Pitfalls
- Treating every scanner hit as a real bug.
- Trusting the scanner to find logic/authz flaws (it won't).
