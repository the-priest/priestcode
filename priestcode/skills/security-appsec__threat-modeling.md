---
name: Threat modeling
description: Threat-model a feature or system before building it.
category: security/appsec
tags: [threat-model, design, stride]
---
# Threat modeling

## When to use
Design phase of anything security-relevant.

## Checklist
- Diagram data flow and trust boundaries.
- Enumerate threats per element (STRIDE: spoofing, tampering, repudiation, info-disclosure, DoS, elevation).
- Rate by likelihood×impact; decide mitigate/accept/transfer.
- Turn top threats into concrete requirements and tests.

## Pitfalls
- A threat model with no follow-through changes nothing — track the mitigations.
- Don't model in a vacuum — include the deployment and the humans.
