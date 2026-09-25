---
name: RAG systems
description: Build retrieval-augmented generation that stays grounded.
category: data-ml
tags: [rag, llm, embeddings]
---
# RAG systems

## When to use
Answering over a document/knowledge base with an LLM.

## Checklist
- Chunk sensibly; embed; retrieve top-k with a real relevance threshold.
- Ground the answer in retrieved text; cite sources; refuse when nothing relevant.
- Evaluate retrieval quality separately from generation.

## Pitfalls
- Retrieving irrelevant chunks → confident hallucination.
- No threshold → always answers even when it shouldn't.
