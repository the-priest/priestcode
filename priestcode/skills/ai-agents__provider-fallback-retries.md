---
name: Provider fallback & retries
description: Keep an LLM app up when a provider fails.
category: ai-agents
tags: [fallback, llm, ai]
---
# Provider fallback & retries

## When to use
Building provider fallback & retries in an LLM app.

## Checklist
- Timeout + retry transient errors with backoff; fall back to another provider/model.
- Surface auth/quota errors clearly; degrade gracefully.
- Make calls idempotent where retried.

## Pitfalls
- No timeout → the app hangs on a stalled provider.
- Retrying non-retryable (400/auth) errors.
