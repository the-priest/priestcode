---
name: Graph traversal
description: Traverse and search graphs correctly.
category: algorithms
tags: [graphs, algorithms]
---
# Graph traversal

## When to use
Working on graph traversal.

## Checklist
- BFS for shortest unweighted path/levels; DFS for reachability/topo/cycles.
- Track visited to avoid infinite loops; Dijkstra/A* for weighted shortest path.
- Pick the representation (adjacency list vs matrix) by density.

## Pitfalls
- No visited set → infinite loops on cycles.
- BFS/DFS where a weighted algorithm is needed.
