"""providers.py — the provider and model catalog.

Priest Code is provider-agnostic: anything that speaks the OpenAI
`/chat/completions` streaming API works. But it is *tuned* for the DeepSeek
V4/V4.1-Flash family — the harness knows their degraded native tool syntax and
their thinking toggle. The catalog below ships three ways to run:

  • deepseek   — SiliconFlow, DeepSeek-V4.1-Flash. The tuned default: fast,
                 cheap, huge context, and the model every harness fix targets.
  • openrouter — a real FREE tier. OpenRouter serves several models at no cost
                 (the `:free` variants); you only need a free OpenRouter key.
  • openai     — a generic escape hatch: point it at any OpenAI-compatible
                 base_url (Ollama, LM Studio, vLLM, Together, Groq, …).

A model carries the two facts the harness needs: whether it is a DeepSeek-style
model whose thinking must be turned OFF for tool use, and whether it exposes a
reasoning-effort dial. Everything else is just an id and a label.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# DeepSeek's peak window (UTC): Mon–Fri 01:00–04:00 and 06:00–10:00. Everything
# else — nights, and all weekend — is off-peak (the cheaper rate). The cost meter
# uses the rate that actually applies right now, so it never over-charges at the
# peak rate outside peak hours.
_PEAK_WINDOWS = ((1.0, 4.0), (6.0, 10.0))


def is_peak(now: Optional[datetime.datetime] = None) -> bool:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if now.weekday() >= 5:            # Sat/Sun → off-peak
        return False
    h = now.hour + now.minute / 60.0
    return any(a <= h < b for a, b in _PEAK_WINDOWS)


def _parse_pair(s: str) -> Optional[Tuple[float, float]]:
    s = (s or "").strip().lower()
    if not s or s == "free":
        return None
    try:
        a, _, b = s.partition("/")
        return (float(a), float(b or a))
    except Exception:
        return None


@dataclass(frozen=True)
class Model:
    id: str
    label: str
    context: int                     # context window, thousands of tokens
    price: str = ""                  # "in/out" USD/1M — the standard (off-peak) rate
    thinking_off: bool = False       # send enable_thinking:false (DeepSeek)
    reasoning_effort: bool = False   # supports a low/high/max dial (GLM etc.)
    note: str = ""
    price_peak: str = ""             # "in/out" USD/1M during peak hours, if different

    def rates(self, now: Optional[datetime.datetime] = None
              ) -> Optional[Tuple[float, float]]:
        """(input, output) USD per 1M tokens that apply RIGHT NOW — the peak rate
        only during peak hours, the standard rate otherwise. None when free."""
        if self.price_peak and is_peak(now):
            r = _parse_pair(self.price_peak)
            if r:
                return r
        return _parse_pair(self.price)

    def cost_usd(self, prompt_tokens: int, completion_tokens: int,
                 now: Optional[datetime.datetime] = None) -> float:
        r = self.rates(now)
        if not r:
            return 0.0
        return (prompt_tokens * r[0] + completion_tokens * r[1]) / 1_000_000.0

    def price_display(self) -> str:
        """Human price for listings: shows both rates when they differ."""
        if self.price_peak and self.price_peak != self.price:
            return f"{self.price} off-peak · {self.price_peak} peak"
        return self.price


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    base_url: str
    key_env: Tuple[str, ...]         # env vars consulted for the key, in order
    models: Tuple[Model, ...] = field(default_factory=tuple)
    signup: str = ""                 # where to get a key
    needs_key: bool = True
    public_token: str = ""           # a fixed token used when no key is set
    #                                  (OpenCode Zen serves free models on
    #                                  `Bearer public` — zero sign-up)

    def model(self, model_id: str) -> Optional[Model]:
        for m in self.models:
            if m.id == model_id:
                return m
        return None

    def default_model(self) -> Model:
        return self.models[0]


# ── SiliconFlow — the full catalog (the tuned home turf) ─────────────
# The DeepSeek family carries thinking_off (enable_thinking:false is required
# for reliable tool use); GLM-5.x carries the reasoning-effort dial. The rest
# are plain OpenAI-compatible chat models. This static list is a good default
# and what the picker shows offline; `priest models --live` fetches whatever
# SiliconFlow is serving right now, so nothing is ever missing.
_SF_MODELS = (
    # DeepSeek — the tuned home turf
    Model("deepseek-ai/DeepSeek-V4.1-Flash", "DeepSeek-V4.1-Flash", 1049,
          "0.15/0.60", thinking_off=True, price_peak="0.30/1.20",
          note="The tuned default. 1M context, trained for tools. "
               "0.15/0.60 off-peak, 0.30/1.20 peak (UTC Mon-Fri 01-04 & 06-10)."),
    Model("deepseek-ai/DeepSeek-V4-Flash", "DeepSeek-V4-Flash", 1049,
          "0.13/0.28", thinking_off=True,
          note="The cheaper benchmarked sibling."),
    Model("deepseek-ai/DeepSeek-V3.2", "DeepSeek-V3.2", 163, "0.26/0.42",
          thinking_off=True, note="Strong general + coding model."),
    Model("deepseek-ai/DeepSeek-V3.1", "DeepSeek-V3.1", 163, "0.27/1.00",
          thinking_off=True, note="Hybrid think/no-think; tools need think off."),
    Model("deepseek-ai/DeepSeek-R1", "DeepSeek-R1", 163, "0.50/2.18",
          note="Reasoning model."),
    Model("deepseek-ai/DeepSeek-V3", "DeepSeek-V3", 128, "0.25/1.00",
          note="The classic V3."),
    # GLM (Zhipu / zai-org)
    Model("zai-org/GLM-5.3-Flash", "GLM-5.3-Flash", 1049, "0.15/0.50",
          reasoning_effort=True, note="Multimodal, long-horizon agent model."),
    Model("zai-org/GLM-4.6", "GLM-4.6", 200, "0.45/1.80",
          reasoning_effort=True, note="Flagship GLM."),
    Model("zai-org/GLM-4.5", "GLM-4.5", 128, "0.45/1.80",
          reasoning_effort=True, note="Agentic GLM."),
    Model("zai-org/GLM-4.5-Air", "GLM-4.5-Air", 128, "0.14/0.86",
          reasoning_effort=True, note="Lighter, cheaper GLM."),
    # Qwen — strong coders
    Model("Qwen/Qwen3-Coder-480B-A35B-Instruct", "Qwen3-Coder-480B", 262,
          "0.45/1.80", note="Top-tier coding model."),
    Model("Qwen/Qwen3-Coder-30B-A3B-Instruct", "Qwen3-Coder-30B", 262,
          "0.07/0.28", note="Fast, cheap coder."),
    Model("Qwen/Qwen3-235B-A22B-Instruct-2507", "Qwen3-235B", 262, "0.35/1.42",
          note="Large general model."),
    Model("Qwen/Qwen3-32B", "Qwen3-32B", 131, "0.07/0.28", note="Balanced."),
    Model("Qwen/QwQ-32B", "QwQ-32B", 131, "0.15/0.58", note="Reasoning model."),
    # Kimi (Moonshot) & MiniMax
    Model("moonshotai/Kimi-K2-Instruct", "Kimi-K2", 128, "0.58/2.29",
          note="Agentic, tool-strong."),
    Model("MiniMaxAI/MiniMax-M1-80k", "MiniMax-M1", 1000, "0.55/2.19",
          note="1M context reasoning model."),
)

# ── OpenRouter — the FREE tier ───────────────────────────────────────
# OpenRouter serves many models at zero cost under the `:free` suffix, but the
# specific ids churn constantly (a model that is free this month is gone the
# next). So the DEFAULT here is the meta-router `openrouter/free`, which
# OpenRouter itself keeps pointed at a live free model AND filters for the
# features the request needs — including tool calling — so native
# function-calling keeps working no matter which concrete model it lands on.
# The named entries below are current-as-of-catalog convenience picks; a stale
# one degrades to a clean error, and `priest models --live` always lists the
# real, current free set.
# NOTE: OpenRouter's `:free` model ids ROTATE (a model that's free this week is
# gone the next). These are ids confirmed live at build time; if one 404s, run
# `priest models --live -P openrouter` for the current set and pick one, or use
# the `openrouter/free` auto-router.
_OR_NEX_PRO_FREE = Model(
    "nex-agi/nex-n2.5-pro:free", "Nex N2.5 Pro (free)", 128, "free",
    note="Free, capable general model. (Free ids rotate — see `models --live`.)")
_OR_LING_FREE = Model(
    "inclusionai/ling-3.0-flash-fin:free", "Ling 3.0 Flash (free)", 128, "free",
    note="Free fast model.")
_OR_NEX_MINI_FREE = Model(
    "nex-agi/nex-n2.5-mini:free", "Nex N2.5 Mini (free)", 128, "free",
    note="Free small/fast model.")
_OR_AUTO_FREE = Model(
    "openrouter/free", "Auto (free router)", 128, "free",
    note="OpenRouter picks a live free model for you. Try this if a specific "
         "free id has rotated out.")


CATALOG: Dict[str, Provider] = {
    "siliconflow": Provider(
        "siliconflow", "SiliconFlow",
        "https://api.siliconflow.com/v1",
        ("PRIEST_API_KEY", "SILICONFLOW_API_KEY", "DEEPSEEK_API_KEY"),
        _SF_MODELS,
        signup="https://siliconflow.com  (create an API key)"),
    "openrouter": Provider(
        "openrouter", "OpenRouter (free tier)",
        "https://openrouter.ai/api/v1",
        ("OPENROUTER_API_KEY", "PRIEST_API_KEY"),
        (_OR_NEX_PRO_FREE, _OR_LING_FREE, _OR_NEX_MINI_FREE, _OR_AUTO_FREE),
        signup="https://openrouter.ai/keys (free key). IMPORTANT for free models: "
               "enable data sharing at openrouter.ai/settings/privacy, or they "
               "return 'no endpoints'. Free ids rotate — `priest models --live`."),
    # ── Google Gemini — the genuinely-free tier that WORKS (no credit card) ──
    # OpenAI-compatible endpoint; a free key from Google AI Studio (a Google
    # login, no card). This is the recommended free option.
    "gemini": Provider(
        "gemini", "Google Gemini (FREE — no credit card)",
        "https://generativelanguage.googleapis.com/v1beta/openai",
        ("GEMINI_API_KEY", "GOOGLE_API_KEY", "PRIEST_API_KEY"),
        (
            Model("gemini-2.5-flash", "Gemini 2.5 Flash (free)", 1000, "free",
                  note="Free, no card. ~15 req/min, 1500/day. The default free pick."),
            Model("gemini-2.5-flash-lite", "Gemini 2.5 Flash-Lite (free)", 1000,
                  "free", note="Fastest/cheapest free tier, highest limits."),
            Model("gemini-2.0-flash", "Gemini 2.0 Flash (free)", 1000, "free",
                  note="Free, solid general model."),
            Model("gemini-2.5-pro", "Gemini 2.5 Pro (free)", 1000, "free",
                  note="Strongest; lower free rate limits."),
        ),
        signup="FREE, no credit card: get a key at aistudio.google.com/apikey "
               "(sign in with Google → Create API key), then run `priest auth`.",
        needs_key=True),
    # ── Groq — free and very fast (free key, no card) ──
    "groq": Provider(
        "groq", "Groq (FREE — fast, no card)",
        "https://api.groq.com/openai/v1",
        ("GROQ_API_KEY", "PRIEST_API_KEY"),
        (
            Model("llama-3.3-70b-versatile", "Llama 3.3 70B (free)", 128, "free",
                  note="Free, fast, capable general model."),
            Model("openai/gpt-oss-120b", "GPT-OSS 120B (free)", 128, "free",
                  note="Large open model, free on Groq."),
            Model("openai/gpt-oss-20b", "GPT-OSS 20B (free)", 128, "free",
                  note="Smaller/faster, free on Groq."),
        ),
        signup="FREE, no credit card: get a key at console.groq.com/keys, "
               "then `priest auth`.",
        needs_key=True),
    # ── OpenCode Zen — requires a Zen API KEY (and billing) for ALL models,
    #    including the free ones. There is NO keyless/public access. ──
    "zen": Provider(
        "zen", "OpenCode Zen (key required)",
        "https://opencode.ai/zen/v1",
        ("OPENCODE_API_KEY", "ZEN_API_KEY", "PRIEST_API_KEY"),
        (
            Model("big-pickle", "Big Pickle (free-tier)", 128, "free",
                  note="No token cost, but a Zen API key is still required."),
            Model("code-supernova", "Code Supernova", 256, "",
                  note="Coding model on Zen."),
            Model("grok-code", "Grok Code", 256, "", note="Coding model on Zen."),
        ),
        signup="Zen needs an API KEY for every model (incl. free ones): sign in "
               "at opencode.ai/zen, add billing, copy the key, then `priest auth`. "
               "For a no-card free option use Google Gemini instead.",
        needs_key=True),
    "openai": Provider(
        "openai", "OpenAI-compatible (custom)",
        "https://api.openai.com/v1",
        ("OPENAI_API_KEY", "PRIEST_API_KEY"),
        (Model("gpt-4o-mini", "gpt-4o-mini", 128, note="Set your own base_url/model."),),
        signup="any OpenAI-compatible endpoint (Ollama, vLLM, Together, Groq…)",
        needs_key=True),
}

DEFAULT_PROVIDER = "siliconflow"


def get_provider(pid: str) -> Optional[Provider]:
    return CATALOG.get(pid)


def resolve(provider_id: str, model_id: str
            ) -> Tuple[Optional[Provider], Optional[Model]]:
    p = CATALOG.get(provider_id)
    if p is None:
        return None, None
    m = p.model(model_id) or (p.default_model() if p.models else None)
    return p, m


def all_models() -> List[Tuple[str, Model]]:
    out: List[Tuple[str, Model]] = []
    for pid, p in CATALOG.items():
        for m in p.models:
            out.append((pid, m))
    return out


def _row_is_free(provider_id: str, model_id: str, row: dict) -> bool:
    """Best-effort 'is this live model free?' across providers."""
    mid = model_id.lower()
    if ":free" in mid or mid.endswith("-free") or "-free-" in mid:
        return True
    # OpenRouter (and many OpenAI-compat catalogs) expose per-token pricing.
    pr = row.get("pricing") if isinstance(row.get("pricing"), dict) else None
    if pr is not None:
        try:
            if float(pr.get("prompt", 0) or 0) == 0 and \
               float(pr.get("completion", 0) or 0) == 0:
                return True
        except Exception:
            pass
    # some catalogs use a boolean/flag
    if row.get("free") is True or str(row.get("cost", "")).lower() == "free":
        return True
    return False


def _row_context(row: dict, default_k: int = 128) -> int:
    for key in ("context_length", "context", "max_context_length"):
        v = row.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return int(v) // 1000 or default_k
    tp = row.get("top_provider")
    if isinstance(tp, dict) and tp.get("context_length"):
        try:
            return int(tp["context_length"]) // 1000 or default_k
        except Exception:
            pass
    return default_k


def live_free_models(provider: "Provider", rows: List[dict]) -> List[Model]:
    """Build Model objects for the FREE models a provider is serving right now,
    from its live /models rows. This is what lets the picker show fresh free
    models and lets a rotated-out default heal itself — no code change needed."""
    out: List[Model] = []
    seen = set()
    for r in rows:
        mid = r.get("id")
        if not mid or mid in seen:
            continue
        if _row_is_free(provider.id, mid, r):
            seen.add(mid)
            label = str(r.get("name") or mid.split("/")[-1])[:40]
            out.append(Model(mid, label, _row_context(r), "free",
                             note="live free model"))
    return out
