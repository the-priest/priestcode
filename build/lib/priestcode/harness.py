"""harness.py — the DeepSeek tool-call canonicaliser.

This is the hard-won core, distilled from a long fight with DeepSeek's tool
syntax in the Basilisk project. The lesson, paid for in bug reports:

  DeepSeek's V4/V4.1-Flash family emit tool calls in their TRAINED native
  syntax — special tokens built from a FULLWIDTH PIPE (｜, U+FF5C) and a ▁
  separator (U+2581):

      <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>read_file
      ```json
      {"path": "main.py"}
      ```<｜tool▁call▁end｜><｜tool▁calls▁end｜>

  Those characters DEGRADE on the way through the tokenizer and the wire: the
  pipe becomes an ASCII `|`, a box `│`, or a doubled `||`; the ▁ separator
  becomes an underscore. A parser that only accepts the canonical glyphs will
  silently fail to see a degraded call — the tool never runs, the model gets
  nothing back, and it loops forever emitting a call the host cannot read.

  So every recogniser here matches a CLASS of pipe characters and a class of
  separators, gated by the literal keyword (`tool`, `invoke`, `function`) so
  that ordinary prose containing `<|x|>` is never mistaken for a call.

The design rule, also learned the hard way: PARSE and STRIP must agree. Every
dialect this file can parse into a call, it must also strip cleanly from the
visible reply — otherwise a call executes but its raw tokens leak onto the
screen, or a call is stripped but never runs. `canonicalise()` is the single
boundary that guarantees it: it rewrites every dialect to ONE form,
`<tool name="x">{json}</tool>`, and everything downstream sees only that.

Native OpenAI `tools`/`tool_calls` function-calling is deliberately NOT used:
it proved less reliable than this text protocol on live SiliconFlow endpoints
(it produced empty `<calls></calls>` wrappers and say-nothing loops). The text
protocol plus this canonicaliser is the reliable path.

Pure, stdlib-only, and unit-tested without a network.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


# ── character classes: the degradations, all of them ─────────────────
_FW_PIPE = "｜"       # ｜ FULLWIDTH VERTICAL LINE  (canonical)
_SEP = "▁"           # ▁ LOWER ONE EIGHTH BLOCK    (canonical separator)

# Every pipe glyph the fullwidth one is seen to degrade into on the wire.
_PIPES = (
    "｜"      # ｜ canonical
    "|"           # ASCII, the documented degradation
    "│"      # │ BOX DRAWINGS LIGHT VERTICAL
    "ǀ"      # ǀ LATIN LETTER DENTAL CLICK (visually identical)
)
_PIPE_CLS = "[" + _PIPES.replace("|", "\\|") + "]"
# The separator degrades too — most often to an underscore.
_SEP_CLS = "[" + _SEP + "_]"


@dataclass
class ToolCall:
    """One decoded tool call. `raw` is True when the JSON body could not be
    parsed — the dispatcher then reports a clean error instead of crashing."""
    name: str
    args: Dict[str, Any] = field(default_factory=dict)
    raw: bool = False


# ── the canonical form everything is rewritten to ───────────────────
_TOOL_TAG_RE = re.compile(
    r'<tool\s+name\s*=\s*"([a-zA-Z_][\w.-]*)"\s*>(.*?)</tool>', re.S)

# a ```json … ``` (or bare ``` … ```) fence around a body
_FENCE_JSON_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)


# ── DeepSeek native tokens, in EVERY degradation ────────────────────
_DS_CALL_RE = re.compile(
    "<" + _PIPE_CLS + r"+tool" + _SEP_CLS + r"call" + _SEP_CLS + r"begin" + _PIPE_CLS + r"+>"
    r"\s*(?:function)?\s*"
    "<" + _PIPE_CLS + r"+tool" + _SEP_CLS + r"sep" + _PIPE_CLS + r"+>"
    r"\s*([A-Za-z_][\w.-]*)\s*"
    r"(.*?)"
    r"(?:<" + _PIPE_CLS + r"+tool" + _SEP_CLS + r"call" + _SEP_CLS + r"end" + _PIPE_CLS + r"+>|$)",
    re.S)

# The wrapper / stray tokens the call regex does not itself consume
# (`<｜tool▁calls▁begin｜>`, `<｜tool▁calls▁end｜>`, a lone `<｜tool▁sep｜>`), in
# every degradation. Safe to widen to the ASCII pipe here — unlike a generic
# `<|…|>` stripper — because the literal `tool` keyword right after the pipe
# makes it unambiguous.
_DS_TOOL_TOKEN_RE = re.compile(
    "<" + _PIPE_CLS + r"+\s*tool" + _SEP_CLS + r"?[^>]*?" + _PIPE_CLS + r"+>", re.I)

# A DeepSeek tool call still ARRIVING mid-stream: from the first tool token to
# end-of-string, once complete calls have been rewritten. Used to hide the raw
# protocol while it streams in.
_DS_PARTIAL_RE = re.compile(
    "<" + _PIPE_CLS + r"+tool" + _SEP_CLS + r".*$", re.S)


# ── DSML invoke dialect: <｜DSML｜invoke name="x"><｜DSML｜parameter …> ──
_DSML_SENTINEL_RE = re.compile(
    "<" + _PIPE_CLS + r"+\s*DSML\s*" + _PIPE_CLS + r"*\s*", re.I)


def _has_dsml(t: str) -> bool:
    return "DSML" in t and bool(_DSML_SENTINEL_RE.search(t))


# ── batch wrappers: <tool_calls> … </tool_calls>, <calls></calls> ────
_WRAPPER_TAG_RE = re.compile(
    r"</?\s*(?:tool_calls?|toolcalls|function_calls?|calls?)\s*>", re.I)
# an EMPTY wrapper the model sometimes emits with nothing inside — pure noise
_EMPTY_WRAPPER_RE = re.compile(
    r"<\s*(calls?|tool_calls?)\s*>\s*</\s*(calls?|tool_calls?)\s*>", re.I)


# ── other XML-ish dialects the model reaches for ────────────────────
_NAME_ATTR_RE = re.compile(r'\bname\s*=\s*"([a-zA-Z_][\w.-]*)"')
_PARAM_RE = re.compile(
    r'<\s*(?:antml:)?parameter\s+name\s*=\s*"([^"]+)"\s*>(.*?)'
    r'</\s*(?:antml:)?parameter\s*>', re.S)

# <invoke name="x"> … </invoke>  and  <tool_call name="x"> … </tool_call> etc.
_ALT_TAG_RES = [
    (re.compile(
        r'<\s*(?:antml:)?(?:invoke|tool_call|toolcall|function_call)\b'
        r'([^>]*)>(.*?)</\s*(?:antml:)?(?:invoke|tool_call|toolcall|function_call)\s*>',
        re.S | re.I), "attrs"),
    (re.compile(r'<\s*function\s*=\s*"?([a-zA-Z_][\w.-]*)"?\s*>(.*?)</\s*function\s*>',
                re.S | re.I), "eqname"),
]
_ALT_OPEN_RE = re.compile(
    r"<\s*(?:antml:)?(?:tool_call|toolcall|function_call|invoke)\b", re.I)
_ALT_CLOSE_RE = re.compile(
    r"<\s*/\s*(?:antml:)?(?:tool_call|toolcall|function_call|invoke)\s*>", re.I)

# GLM-style <tool_call>name<arg_key>k</arg_key><arg_value>v</arg_value></tool_call>
_ARG_KV_RE = re.compile(
    r"<arg_key>\s*(.*?)\s*</arg_key>\s*<arg_value>\s*(.*?)\s*</arg_value>", re.S)


def _body_to_json(body: str) -> str:
    """Pull a JSON object out of a tool body — bare, fenced, or with slop
    around it — and return it as a compact JSON string. Falls back to `{}`."""
    body = (body or "").strip()
    fm = _FENCE_JSON_RE.search(body)
    if fm:
        body = fm.group(1).strip()
    if not body:
        return "{}"
    # already a clean object?
    if body[0] == "{":
        b, e = body.find("{"), body.rfind("}")
        if b != -1 and e > b:
            return body[b:e + 1]
    b, e = body.find("{"), body.rfind("}")
    if b != -1 and e > b:
        return body[b:e + 1]
    return "{}"


def _glm_kv_to_json(body: str) -> str:
    pairs = _ARG_KV_RE.findall(body or "")
    if not pairs:
        return _body_to_json(body)
    out: Dict[str, Any] = {}
    for k, v in pairs:
        v = v.strip()
        try:
            out[k.strip()] = json.loads(v)
        except Exception:
            out[k.strip()] = v
    return json.dumps(out)


def canonicalise(text: str) -> str:
    """Rewrite every known tool-call dialect to the single canonical form
    `<tool name="x">{json}</tool>`. Conservative: only shapes that unambiguously
    ARE tool calls are rewritten, so prose is never turned into a call. Idempotent
    — running it twice yields the same result — which is what lets it run at one
    boundary and be trusted everywhere downstream.
    """
    if not text or "<" not in text:
        return text
    out = text

    # 0. DSML sentinel first: strip `<｜DSML｜｜` down to `<`, then the rest of
    #    this function sees ordinary markup it understands.
    if _has_dsml(out):
        out = _DSML_SENTINEL_RE.sub("<", out)

    # 0b. empty and batch wrappers
    if "calls" in out.lower():
        out = _EMPTY_WRAPPER_RE.sub("", out)
        out = _WRAPPER_TAG_RE.sub("", out)

    # 1. DeepSeek native tokens (any pipe/separator degradation)
    if _FW_PIPE in out or _has_ds_tool_token(out):
        def _ds(m: "re.Match") -> str:
            name = m.group(1)
            return f'<tool name="{name}">{_body_to_json(m.group(2))}</tool>'
        out = _DS_CALL_RE.sub(_ds, out)
        out = _DS_TOOL_TOKEN_RE.sub("", out)

    # 2. GLM arg_key/arg_value inside <tool_call>name…</tool_call>
    if "<arg_key>" in out and "<tool_call>" in out:
        def _glm(m: "re.Match") -> str:
            inner = m.group(1)
            nm = re.match(r"\s*([a-zA-Z_][\w.-]*)", inner)
            name = nm.group(1) if nm else ""
            if not name:
                return m.group(0)
            return f'<tool name="{name}">{_glm_kv_to_json(inner)}</tool>'
        out = re.sub(r"<tool_call>(.*?)</tool_call>", _glm, out, flags=re.S)

    # 3. other tag dialects: <invoke name=…>, <tool_call name=…>, <function=…>
    for rx, kind in _ALT_TAG_RES:
        def _alt(m: "re.Match", kind=kind) -> str:
            if kind == "eqname":
                name, body = m.group(1), m.group(2)
            else:
                attrs, body = m.group(1) or "", m.group(2) or ""
                nm = _NAME_ATTR_RE.search(attrs)
                if not nm:
                    return m.group(0)
                name = nm.group(1)
            # <parameter name=…> children → JSON
            params = _PARAM_RE.findall(body)
            if params:
                obj: Dict[str, Any] = {}
                for k, v in params:
                    v = v.strip()
                    try:
                        obj[k] = json.loads(v)
                    except Exception:
                        obj[k] = v
                return f'<tool name="{name}">{json.dumps(obj)}</tool>'
            return f'<tool name="{name}">{_body_to_json(body)}</tool>'
        out = rx.sub(_alt, out)

    return out


def _has_ds_tool_token(t: str) -> bool:
    """Cheap gate: is a DeepSeek tool token (any degradation) present? The
    `tool` substring check is a fast literal reject before any regex runs."""
    if not t or "tool" not in t:
        return False
    return bool(_DS_TOOL_TOKEN_RE.search(t)) or bool(_DS_CALL_RE.search(t))


def parse_tool_calls(text: str) -> List[ToolCall]:
    """Return every tool call in `text`, decoding all dialects first."""
    if not text:
        return []
    norm = canonicalise(text)
    calls: List[ToolCall] = []
    for m in _TOOL_TAG_RE.finditer(norm):
        name = m.group(1)
        body = (m.group(2) or "").strip()
        try:
            args = json.loads(body) if body else {}
            if not isinstance(args, dict):
                args = {"value": args}
            calls.append(ToolCall(name=name, args=args))
        except Exception:
            calls.append(ToolCall(name=name, args={"_raw": body}, raw=True))
    return calls


def strip_tool_calls(text: str) -> str:
    """Remove canonical `<tool …>` blocks from a reply, leaving the prose. Run
    on canonicalised text so it removes exactly what `parse_tool_calls` found."""
    if not text:
        return text
    norm = canonicalise(text)
    return _TOOL_TAG_RE.sub("", norm)


# Debris that means "the model TRIED to call a tool and we could not read it" —
# used only when a turn produced no parseable calls, to hide raw protocol and,
# optionally, ask the model to re-emit.
_DEBRIS_RES = [
    re.compile(r"<\s*/?\s*tool\b", re.I),
    re.compile(r"</?\s*(?:tool_call|toolcall|function_call|invoke)\b", re.I),
    re.compile(r"<\s*/?\s*" + _PIPE_CLS + r"+\s*DSML", re.I),
    re.compile("<" + _PIPE_CLS + r"+\s*tool" + _SEP_CLS, re.I),
    re.compile("<" + _FW_PIPE),
    re.compile(r"<\s*function\s*=", re.I),
    re.compile(r"<\s*(?:antml:)?parameter\b[^>]*\bname\s*=", re.I),
]


def scrub_debris(text: str) -> str:
    """Blank out lines that are pure unparsed tool-call debris, so a call the
    canonicaliser could not decode never reaches the screen as raw tokens."""
    if not text:
        return text
    # hide a DeepSeek call still arriving mid-stream
    text = _DS_PARTIAL_RE.sub("", text)
    text = _EMPTY_WRAPPER_RE.sub("", text)
    kept = []
    for line in text.splitlines():
        if any(rx.search(line) for rx in _DEBRIS_RES):
            continue
        kept.append(line)
    return "\n".join(kept)


def clean_reply(text: str) -> str:
    """The visible reply: canonical calls removed, debris scrubbed, trimmed."""
    return scrub_debris(strip_tool_calls(text or "")).strip()


def looks_like_failed_call(text: str) -> bool:
    """True when the reply carries tool-call debris but parsed to no call — the
    model tried to call something and we could not read it."""
    if parse_tool_calls(text):
        return False
    return bool(text) and any(rx.search(text) for rx in _DEBRIS_RES)
