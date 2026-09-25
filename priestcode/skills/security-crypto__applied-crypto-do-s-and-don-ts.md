---
name: Applied crypto do's and don'ts
description: Use cryptography correctly — pick the right primitive, use it right.
category: security/crypto
tags: [crypto, encryption, hashing]
---
# Applied crypto do's and don'ts

## When to use
Any time you reach for encryption, hashing, signing, or randomness.

## Checklist
- Encryption: authenticated (AES-GCM / libsodium secretbox); never ECB; unique nonce per message.
- Passwords: argon2/bcrypt/scrypt — a slow KDF with a salt, never a fast hash.
- Integrity/signatures: HMAC or Ed25519; constant-time compare.
- Randomness: a CSPRNG (secrets/os.urandom), never `random`.
- Keys: from a KDF or generated; stored in a secret manager.

## Pitfalls
- Never invent a scheme or 'encrypt' with XOR/base64.
- Nonce reuse in GCM/CTR is catastrophic.
- `==` on secrets leaks via timing — use a constant-time compare.

## Example
# python: from cryptography.hazmat ... AESGCM; or PyNaCl SecretBox
