---
name: Streaming responses
description: Stream model output to the UI correctly.
category: ai-agents
tags: [streaming, llm, ai]
---
# Streaming responses

## When to use
Building streaming responses in an LLM app.

## Checklist
- Parse SSE/deltas incrementally; flush tokens to the UI as they arrive.
- Accumulate tool-call fragments by index/id; handle [DONE] and errors mid-stream.
- Don't block the UI thread; handle cancellation.

## Pitfalls
- Buffering the whole response defeats streaming.
- Mishandling partial tool-call chunks.
