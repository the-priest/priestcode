---
name: Model evaluation
description: Evaluate ML models honestly.
category: data-ml
tags: [ml, evaluation]
---
# Model evaluation

## When to use
Assessing whether a model actually works.

## Checklist
- Hold out a real test set; no leakage from train into features/preprocessing.
- Pick metrics that match the problem (not just accuracy on imbalanced data).
- Compare to a baseline; check per-slice performance and calibration.

## Pitfalls
- Data leakage inflates offline metrics that collapse in prod.
- Accuracy on imbalanced data is misleading.
