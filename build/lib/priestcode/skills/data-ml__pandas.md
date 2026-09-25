---
name: pandas
description: Manipulate tabular data correctly and fast with pandas.
category: data-ml
tags: [pandas, python, data]
---
# pandas

## When to use
Analyzing/transforming tabular data in Python.

## Checklist
- Vectorize — avoid iterrows/apply in hot paths; use built-in ops.
- Handle NaN and dtypes explicitly; avoid chained-assignment (use .loc).
- Merge/groupby correctly; check row counts after joins.
- Validate the shape/schema of inputs and outputs.

## Pitfalls
- SettingWithCopy from chained indexing corrupts data silently.
- iterrows is orders of magnitude slower than vectorized ops.
