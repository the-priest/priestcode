"""client.py — the OpenAI-compatible streaming client.

One job: turn a messages list into a streamed reply, correctly, for any
OpenAI-`/chat/completions` provider. Everything hard-won from the Basilisk
project lives here:

  • enable_thinking:false for the DeepSeek family — REQUIRED for reliable tool
    use, and the difference between a model that acts and one that "thinks for
    50,000 characters and says nothing".
  • The structured `delta.tool_calls` channel is read AND folded to canonical
    `<tool …>` text that is emitted through the SAME token callback the content
    uses — because the frontend buffers tokens and parses that buffer. Putting a
    synthesized call only in the final payload (and not on the token stream) is
    exactly the bug that made a perfect call read as an empty, "degraded" turn.
  • A degraded/empty reply is retried a bounded number of times, and 5xx / rate
    limits surface as clean errors, never a crash.

stdlib only: urllib for the POST, no SDK.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from . import harness
from .providers import Model, Provider


@dataclass
class Completion:
    text: str = ""
    finish_reason: str = ""
    truncated: bool = False
    error: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0
    # Native (OpenCode-style) structured tool calls: each is
    # {"id": str, "name": str, "arguments": str-json}. Populated when the
    # request carried a `tools` schema and the model replied with tool_calls.
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tools_unsupported: bool = False   # provider rejected the tools field


def _render_tool_calls(acc: Dict[int, Dict[str, str]]) -> str:
    """Fold accumulated structured tool_calls into canonical <tool …> text."""
    out = []
    for i in sorted(acc):
        slot = acc[i]
        name = (slot.get("name") or "").strip()
        args = slot.get("args") or ""
        if not name:
            continue
        body = args.strip() or "{}"
        # validate/normalise the JSON body if we can
        try:
            body = json.dumps(json.loads(body))
        except Exception:
            pass
        out.append(f'<tool name="{name}">{body}</tool>')
    return "\n".join(out)


class Client:
    def __init__(self, provider: Provider, base_url: str, api_key: str,
                 timeout: float = 300.0):
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def list_models_live(self) -> list:
        """GET /models — the provider's live catalog (ids). [] on any failure,
        so the picker always has the static list to fall back to."""
        url = self.base_url + "/models"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("data") if isinstance(data, dict) else data
            return [r.get("id") for r in rows if isinstance(r, dict) and r.get("id")]
        except Exception:
            return []

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        # OpenRouter likes these; harmless elsewhere.
        h["HTTP-Referer"] = "https://github.com/the-priest/priestcode"
        h["X-Title"] = "Priest Code"
        return h

    def stream(self, model: Model, messages: List[Dict[str, Any]],
               on_token: Callable[[str], None],
               on_reasoning: Optional[Callable[[str], None]] = None,
               *, temperature: float = 0.3, top_p: float = 0.95,
               max_tokens: int = 16384,
               reasoning_effort: str = "low",
               tools: Optional[List[Dict[str, Any]]] = None,
               cancel: Optional[Callable[[], bool]] = None) -> Completion:
        """Stream one completion.

        NATIVE function-calling (the OpenCode way): when `tools` (a list of
        OpenAI function schemas) is passed, it goes in the request and the
        model's structured `tool_calls` come back in `Completion.tool_calls`,
        each `{id, name, arguments}` — the caller round-trips them as
        `role:"tool"` messages. Content still streams through `on_token`,
        reasoning through `on_reasoning`. If the provider rejects the `tools`
        field, `Completion.tools_unsupported` is set so the caller can fall back
        to the text protocol.
        """
        body: Dict[str, Any] = {
            "model": model.id,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True,
        }
        # DeepSeek REQUIRES thinking off to use the function-call feature — and
        # off is the right default for tool use across the family anyway.
        if model.thinking_off:
            body["enable_thinking"] = False
        if model.reasoning_effort:
            body["reasoning_effort"] = reasoning_effort
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"

        return self._attempt(body, on_token, on_reasoning, cancel,
                             native=bool(tools))

    def _attempt(self, body, on_token, on_reasoning, cancel,
                 native=False) -> Completion:
        url = self.base_url + "/chat/completions"
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._headers(),
                                     method="POST")
        started = time.time()
        parts: List[str] = []
        tc_acc: Dict[int, Dict[str, str]] = {}
        finish = ""
        comp = Completion()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                for raw in resp:
                    if cancel and cancel():
                        break
                    line = raw.decode("utf-8", "replace").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        obj = json.loads(payload)
                    except Exception:
                        continue
                    ch = (obj.get("choices") or [{}])[0]
                    delta = ch.get("delta") or {}
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
                    # reasoning
                    rc = delta.get("reasoning_content")
                    if rc and on_reasoning:
                        on_reasoning(rc)
                    # content
                    tok = delta.get("content")
                    if tok:
                        parts.append(tok)
                        on_token(tok)
                    # structured tool calls (accumulated by index, id captured)
                    for tc in (delta.get("tool_calls") or []):
                        fn = tc.get("function") or {}
                        idx = tc.get("index")
                        if idx is None:
                            idx = len(tc_acc)
                        if (fn.get("name") and idx in tc_acc
                                and tc_acc[idx].get("name")
                                and fn["name"] != tc_acc[idx]["name"]):
                            # a genuinely DIFFERENT call reusing the index → new
                            # slot. Only split when the name actually differs:
                            # some providers resend function.name on every chunk
                            # of the SAME call, and splitting those produced two
                            # half-JSON slots with a colliding id.
                            idx = max(tc_acc) + 1 if tc_acc else 0
                        slot = tc_acc.setdefault(idx, {"id": "", "name": "", "args": ""})
                        if tc.get("id"):
                            slot["id"] = tc["id"]
                        if fn.get("name"):
                            slot["name"] = fn["name"]
                        if fn.get("arguments"):
                            slot["args"] += fn["arguments"]
                    # usage (some providers send it on the last frame)
                    if obj.get("usage"):
                        u = obj["usage"]
                        comp.prompt_tokens = u.get("prompt_tokens", 0) or 0
                        comp.completion_tokens = u.get("completion_tokens", 0) or 0
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode("utf-8", "replace")[:400]
            except Exception:
                pass
            # A provider that does not support the `tools` field: strip it and
            # retry once on the text protocol rather than failing the turn.
            low = (detail or "").lower()
            if (e.code in (400, 422) and native and body.get("tools")
                    and any(w in low for w in
                            ("tool", "function", "tool_choice"))):
                body.pop("tools", None)
                body.pop("tool_choice", None)
                comp = self._attempt(body, on_token, on_reasoning, cancel,
                                     native=False)
                comp.tools_unsupported = True
                return comp
            comp.error = self._explain_http(e.code, detail)
            return comp
        except urllib.error.URLError as e:
            comp.error = f"network error: {e.reason}"
            return comp
        except Exception as e:  # pragma: no cover - defensive
            comp.error = f"{type(e).__name__}: {e}"
            return comp

        comp.text = "".join(parts)
        if native:
            # NATIVE PATH: hand the structured calls back as-is. The agent will
            # round-trip them as an assistant.tool_calls message + role:"tool"
            # results — the OpenCode contract. No text synthesis.
            for i in sorted(tc_acc):
                slot = tc_acc[i]
                name = (slot.get("name") or "").strip()
                if not name:
                    continue
                comp.tool_calls.append({
                    "id": slot.get("id") or f"call_{i}",
                    "name": name,
                    "arguments": slot.get("args") or "{}"})
        elif tc_acc:
            # FALLBACK (text protocol): a provider that ignored `tools` but still
            # streamed structured calls — fold them into canonical <tool> text so
            # the text parser sees them (the harness path).
            synth = _render_tool_calls(tc_acc)
            if synth and not harness.parse_tool_calls(comp.text):
                on_token(synth)
                comp.text += synth
        comp.finish_reason = finish
        comp.truncated = finish == "length"
        comp.seconds = time.time() - started
        return comp

    @staticmethod
    def _explain_http(code: int, detail: str) -> str:
        if code in (401, 403):
            return ("authentication failed — check your API key "
                    "(`priest auth`).")
        if code == 402:
            return "payment required — this model/provider needs credit."
        if code == 429:
            return "rate limited — wait a moment and retry."
        if 500 <= code < 600:
            return f"provider error (HTTP {code}) — usually transient, retry."
        # surface a short reason for a 400/404 (bad model id, bad field)
        reason = detail.strip().replace("\n", " ")[:200] if detail else ""
        return f"HTTP {code}{': ' + reason if reason else ''}"
