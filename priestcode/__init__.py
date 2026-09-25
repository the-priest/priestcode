"""Priest Code — a supreme terminal coding agent.

A fast, transparent, provider-agnostic coding tool: it opens your repo, reads
it, edits it, runs your tests, and iterates until they pass — and it shows you
every step as it happens. Born from connecting two ideas: OpenCode's clean
terminal-app architecture and the Basilisk project's hard-won model harness
(the tool-call canonicaliser that survives DeepSeek's degraded native syntax,
thinking-off, and the streaming corrections that keep an agent loop from
stalling).

Tuned hardest for DeepSeek-V4.1-Flash, but it speaks any OpenAI-compatible
provider — including free tiers.
"""

__version__ = "1.2.0"
__all__ = ["__version__"]
