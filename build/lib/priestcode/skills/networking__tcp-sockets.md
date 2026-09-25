---
name: TCP sockets
description: Write correct TCP socket code.
category: networking
tags: [sockets, networking]
---
# TCP sockets

## When to use
Working with tcp sockets.

## Checklist
- Handle partial reads/writes (loop until done); set timeouts; framing for messages.
- Clean shutdown/close; handle RST/EOF; back-pressure on slow peers.
- Non-blocking or threads for many connections.

## Pitfalls
- Assuming one recv == one message (TCP is a stream).
- No timeout → hung forever on a dead peer.
