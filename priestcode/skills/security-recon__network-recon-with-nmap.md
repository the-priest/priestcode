---
name: Network recon with nmap
description: Discover hosts, ports, and services with nmap effectively.
category: security/recon
tags: [nmap, recon, scanning, ports]
---
# Network recon with nmap

## When to use
Start of an authorized engagement — map the attack surface.

## Checklist
- Host discovery first (`-sn`) on the scope, then port scan live hosts.
- Service/version + default scripts on found ports (`-sV -sC`).
- Tune timing (`-T4`) and scope; full TCP (`-p-`) when time allows, top-ports when not.
- Save all formats (`-oA`) for later parsing.

## Pitfalls
- `-T5` drops results on flaky links; `-T4` is the safer default.
- UDP scanning is slow and noisy — target known UDP services.
- Scanning out of scope is illegal — confirm the ROE.

## Example
nmap -sV -sC -T4 -p- -oA scan target   # authorized scope only
