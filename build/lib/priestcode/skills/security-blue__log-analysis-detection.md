---
name: Log analysis & detection
description: Hunt for intrusion in logs and build detections.
category: security/blue
tags: [blue-team, logs, detection, dfir]
---
# Log analysis & detection

## When to use
Incident response or building detections.

## Checklist
- Baseline normal, then hunt anomalies: auth failures/spikes, new admin, odd process trees, beaconing.
- Correlate across sources (auth, web, EDR, DNS) on time and identity.
- Turn a confirmed pattern into a durable detection rule.
- Preserve evidence; document timeline.

## Pitfalls
- Clock skew across sources breaks correlation — normalize to UTC.
- Attackers clear logs — ship logs off-host.
