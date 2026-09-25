---
name: Insecure deserialization
description: Find and fix unsafe deserialization leading to RCE or object injection.
category: security/web
tags: [deserialization, rce, pickle, owasp]
---
# Insecure deserialization

## When to use
Any place untrusted bytes are deserialized: pickle, PHP unserialize, Java readObject, YAML load.

## Checklist
- Find the sink: `pickle.loads`, `yaml.load` (unsafe), Java `ObjectInputStream`, PHP `unserialize`.
- Build a gadget-chain payload for the language/framework to prove impact.
- FIX: never deserialize untrusted data with these; use JSON / safe loaders; sign+verify if you must.

## Pitfalls
- `yaml.load` without SafeLoader executes arbitrary objects — use `yaml.safe_load`.
- Pickle is not a data format for untrusted input, ever.

## Example
# safe: yaml.safe_load(x); json.loads(x)  # never pickle.loads(untrusted)
