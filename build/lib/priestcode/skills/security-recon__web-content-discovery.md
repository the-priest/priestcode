---
name: Web content discovery
description: Find hidden endpoints, files, and parameters on a web target.
category: security/recon
tags: [fuzzing, web, recon, ffuf, gobuster]
---
# Web content discovery

## When to use
Enumerating a web app's hidden surface.

## Checklist
- Directory/file brute force with a good wordlist (SecLists), filter by size/status.
- Vhost and subdomain enumeration; check robots.txt, sitemap, JS files for endpoints.
- Parameter discovery (arjun/ffuf) on interesting endpoints.
- Grep JS bundles for API paths, keys, and comments.

## Pitfalls
- Filter out the false-positive size (soft 404s) or you drown in noise.
- Rate-limit to avoid taking the target down / getting blocked.

## Example
ffuf -u https://t/FUZZ -w wordlist.txt -mc 200,301,302,403 -fs 0
