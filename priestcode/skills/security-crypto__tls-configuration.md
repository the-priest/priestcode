---
name: TLS configuration
description: TLS configuration: find, exploit (authorized), and fix.
category: security/crypto
tags: [tls, crypto, hardening]
---
# TLS configuration

## When to use
Configuring or reviewing TLS for a service.

## Checklist
- Modern protocols only (TLS 1.2/1.3); strong cipher suites; disable renegotiation/compression.
- Valid cert chain; HSTS; OCSP stapling; test with an SSL scanner.
- Rotate keys; protect private keys.

## Pitfalls
- Old protocols/ciphers (SSLv3, RC4) break confidentiality.
- Self-signed/expired certs train users to ignore warnings.
