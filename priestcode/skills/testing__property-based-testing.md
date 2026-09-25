---
name: Property-based testing
description: Find edge cases with generated inputs.
category: testing
tags: [property-testing, hypothesis, fuzzing]
---
# Property-based testing

## When to use
Logic with a wide input space (parsers, encoders).

## Checklist
- State invariants that must always hold; let the framework generate inputs (Hypothesis/fast-check).
- Use round-trip properties (decode(encode(x))==x); shrink failing cases.
- Add discovered failures as explicit regression tests.

## Pitfalls
- Weak properties that always pass prove nothing.
- Nondeterministic properties without seeds.
