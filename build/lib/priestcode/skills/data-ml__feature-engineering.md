---
name: Feature engineering
description: Build features that help a model without leaking.
category: data-ml
tags: [ml, features]
---
# Feature engineering

## When to use
Preparing inputs for a model.

## Checklist
- Derive features from domain knowledge; fit transforms on TRAIN only, apply to test.
- Handle missing values and scaling consistently; avoid target leakage.
- Validate feature distributions train vs serve.

## Pitfalls
- Fitting scalers/encoders on the whole dataset leaks test info.
- Train/serve skew from inconsistent transforms.
