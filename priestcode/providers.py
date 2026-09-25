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

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Model:
    id: str
    label: str
    context: int                     # context window, thousands of tokens
    price: str = ""                  # "in/out" USD per 1M tokens, or "free"/""
    thinking_off: bool = False       # send enable_thinking:false (DeepSeek)
    reasoning_effort: bool = False   # supports a low/high/max dial (GLM etc.)
    note: str = ""

    def rates(self) -> Optional[Tuple[float, float]]:
        """(input, output) USD per 1M tokens, or None when free/unknown — so the
        cost meter shows real spend and nothing for free models."""
        p = (self.price or "").strip().lower()
        if not p or p == "free":
            return None
        try:
            a, _, b = p.partition("/")
            return (float(a), float(b or a))
        except Exception:
            return None

    def cost_usd(self, prompt_tokens: int, completion_tokens: int) -> float:
        r = self.rates()
        if not r:
            return 0.0
        return (prompt_tokens * r[0] + completion_tokens * r[1]) / 1_000_000.0


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
          "0.30/1.20", thinking_off=True,
          note="The tuned default. 1M context, trained for tools."),
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
_OR_AUTO_FREE = Model(
    "openrouter/free", "Auto (free, tool-capable)", 128, "free",
    note="OpenRouter picks a live FREE model that supports tools. Robust default.")
_OR_GLM_FREE = Model(
    "z-ai/glm-5.2:free", "GLM 5.2 (free)", 200, "free",
    reasoning_effort=True, note="Free flagship-class GLM; strong agent model.")
_OR_QWEN_FREE = Model(
    "qwen/qwen3.8-27b:free", "Qwen3.8 27B (free)", 128, "free",
    note="Free general/coding model.")
_OR_NEMOTRON_FREE = Model(
    "nvidia/nemotron-3-super-120b-a12b:free", "Nemotron 3 Super 120B (free)",
    128, "free", note="Free large NVIDIA model.")


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
        (_OR_AUTO_FREE, _OR_GLM_FREE, _OR_QWEN_FREE, _OR_NEMOTRON_FREE),
        signup="https://openrouter.ai/keys  (free key; free models cost $0)"),
    "zen": Provider(
        "zen", "OpenCode Zen (free, no sign-up)",
        "https://opencode.ai/zen/v1",
        ("OPENCODE_API_KEY", "ZEN_API_KEY", "PRIEST_API_KEY"),
        (
            Model("muse-spark-1.3-contributor-free", "Muse Spark 1.3 (free)",
                  128, "free",
                  note="Free on Zen, no sign-up. The default Zen pick."),
            Model("deepseek-v4-flash-free", "DeepSeek-V4-Flash (free)", 1049,
                  "free", thinking_off=True,
                  note="Free on Zen — the exact family the harness is tuned for."),
            Model("mimo-v2.5-free", "MiMo V2.5 (free)", 128, "free",
                  note="Free coding model on Zen."),
            Model("nemotron-3.5-lightning-free", "Nemotron 3.5 Lightning (free)",
                  128, "free", note="Free fast model on Zen."),
            Model("big-pickle", "Big Pickle (free)", 128, "free",
                  note="Free experimental model on Zen."),
        ),
        signup="https://opencode.ai/zen  — free models need NO key (a fixed "
               "`public` token is used). `priest models --live` lists the "
               "current free set (they rotate).",
        needs_key=False,
        public_token="public"),
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
