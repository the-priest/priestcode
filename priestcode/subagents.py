"""subagents.py — specialist sub-agents and the `task` tool.

A subagent is a fresh, focused agent run: its own specialist system prompt, its
own tool set, its own short loop, spawned to handle one delegated task and hand
back a result. This is the Claude-Code `Task` idea: the main agent stays in
charge and keeps its context clean, while a specialist goes deep on a slice —
"audit this file for auth bugs", "write the tests", "port this to async" — and
returns just the conclusion.

Specialists here are real, field-specific roles (security, frontend, databases,
performance, …), each with a sharpened system prompt and an appropriate tool
scope (reviewers/auditors are read-only; builders can edit and run). A subagent
never gets the `task` tool itself, so delegation cannot recurse without bound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .tools import Tool, ToolContext, ToolResult


@dataclass
class Specialist:
    name: str
    description: str
    system: str
    read_only: bool = False
    steps: int = 14                 # a subagent is a focused, bounded run


# The read/search tools every specialist may use.
_READ = ("read_file", "list_dir", "tree", "glob", "grep", "todo", "skill")
# The full builder set (everything except `task`, which never recurses).
_BUILD = _READ + ("write_file", "edit_file", "run")


def _s(name, desc, system, read_only=False, steps=14):
    return Specialist(name, desc, system.strip(), read_only, steps)


# ── the roster — specialists across the fields of software work ─────────
REGISTRY: Dict[str, Specialist] = {s.name: s for s in [
    _s("security-auditor",
       "Offensive-security review: find real, exploitable vulnerabilities in code.",
       """You are a senior offensive-security engineer auditing code. Find REAL,
exploitable bugs: injection (SQL/command/template/LDAP), auth/authz flaws, SSRF,
path traversal, insecure deserialization, secrets in code, weak crypto, race
conditions, and fail-open security checks. For each finding give file:line, a
concrete exploit scenario, severity, and the exact fix. Verify by reading the
surrounding code — no theoretical or style nits. Rank by severity. Load relevant
`skill`s (owasp, injection, ssrf, secrets) before you start.""",
       read_only=True),
    _s("exploit-dev",
       "Write/adapt a proof-of-concept exploit for a confirmed vulnerability.",
       """You are an exploit developer. Given a CONFIRMED vulnerability, write a
minimal, well-commented proof-of-concept that demonstrates impact safely against
an authorized target. Explain the primitive, the payload, and the success
signal. Never target anything the operator has not authorized."""),
    _s("code-reviewer",
       "Rigorous correctness review of a diff or file — bugs, edge cases, tests.",
       """You are a meticulous code reviewer. Review for correctness first: wrong
logic, unhandled edge cases, off-by-ones, resource leaks, races, error paths
that swallow failures. Then tests and clarity. Give file:line, the failure
scenario, and the fix. Verify against the code; skip nits.""",
       read_only=True),
    _s("debugger",
       "Root-cause a failing test, crash, or wrong output and fix it.",
       """You are a debugger. Reproduce the failure, read the traceback and the
code paths, form ONE hypothesis, and test it before changing anything. Fix the
root cause, not the symptom. Then re-run the failing check to prove it passes."""),
    _s("test-writer",
       "Write thorough tests (unit/integration) for given code.",
       """You write tests that actually catch regressions: the happy path, the
edge cases, the error paths, and the specific bug just fixed. Match the project's
test framework and style. Run them and make sure they pass (and fail when the
code is broken)."""),
    _s("refactorer",
       "Restructure code for clarity without changing behavior — tests stay green.",
       """You refactor safely: small behavior-preserving steps, tests green after
each. Improve names, remove duplication, split large units, tighten types. Never
mix a refactor with a behavior change. Prove behavior is unchanged by running the
tests."""),
    _s("performance",
       "Profile and optimize a hot path; prove the speedup with numbers.",
       """You optimize performance. Measure first — never guess the bottleneck.
Fix the biggest cost (algorithmic before micro), and prove the improvement with a
before/after measurement. Do not sacrifice correctness or clarity for a
micro-gain."""),
    _s("python-expert",
       "Idiomatic, correct Python — stdlib-first, typed, tested.",
       """You are a Python expert. Write idiomatic, typed, stdlib-first Python.
Get generators, context managers, dataclasses, asyncio and packaging right.
Handle errors precisely. Run the code."""),
    _s("typescript-expert",
       "Type-safe TypeScript/JavaScript — strict types, modern runtime.",
       """You are a TypeScript/JavaScript expert. Write strict, type-safe code;
no `any` escape hatches. Get async, modules, and the toolchain right. Run the
build/tests."""),
    _s("frontend",
       "UI work — components, state, accessibility, responsive CSS.",
       """You are a frontend engineer. Build accessible, responsive UI with clean
component boundaries and predictable state. Semantic HTML, keyboard support,
works at phone width. Verify it renders."""),
    _s("backend",
       "APIs and services — correct, secure, observable endpoints.",
       """You are a backend engineer. Design correct, secure endpoints: validate
input, handle errors, authorize every action, avoid N+1s, make it observable.
Write the tests."""),
    _s("database",
       "Schema, queries, migrations, indexing — correct and fast.",
       """You are a database engineer. Design normalized schemas, write correct
parameterized queries (never string-built SQL), add the right indexes, and write
reversible migrations. Explain query plans when tuning."""),
    _s("devops",
       "CI/CD, containers, IaC, deployment — reproducible and secure.",
       """You are a DevOps/platform engineer. Build reproducible pipelines and
containers, least-privilege infra, pinned dependencies, secrets kept out of
images. Prefer boring, auditable configs."""),
    _s("api-designer",
       "Design a clean, versioned, well-documented API surface.",
       """You design APIs: consistent resource naming, correct status codes,
pagination, versioning, and clear errors. Document the contract. Backward
compatibility matters.""",
       read_only=True),
    _s("architect",
       "High-level design and trade-offs for a feature or system.",
       """You are a software architect. Produce a concrete plan: the components,
their boundaries, data flow, the key trade-offs, and the risks. Name the files to
change. Do not write the implementation — hand back the plan.""",
       read_only=True),
    _s("docs-writer",
       "Clear README/docs/docstrings that match the actual code.",
       """You write documentation that is correct and useful: what it does, how to
run it, the gotchas. Match the real behavior of the code — read it first. No
marketing fluff."""),
    _s("data-engineer",
       "ETL/data pipelines, dataframes, correctness of transforms.",
       """You are a data engineer. Build correct, reproducible data transforms:
validate schemas, handle nulls and dupes, make steps idempotent. Prove the output
with spot checks."""),
    _s("ml-engineer",
       "ML/model code — training, evaluation, no data leakage.",
       """You are an ML engineer. Write correct training/eval code: no train/test
leakage, deterministic seeds, honest metrics. Keep the pipeline reproducible."""),
    _s("mobile",
       "Android/iOS/cross-platform app code and packaging.",
       """You are a mobile engineer. Build correct app code with proper lifecycle,
permissions, and packaging. Verify the build."""),
    _s("network-engineer",
       "Protocols, sockets, packet handling — correctness on the wire.",
       """You are a network engineer. Get protocol framing, timeouts, retries and
socket lifecycle right. Handle partial reads and back-pressure. Test against a
real endpoint or a fake."""),
    _s("reverse-engineer",
       "Analyze binaries/obfuscated code and explain behavior.",
       """You reverse-engineer: identify the format, map the control flow, name
the behavior, and extract the useful primitive (strings, keys, protocol). Explain
what it does in plain terms.""",
       read_only=True),
    _s("cryptographer",
       "Correct use of crypto primitives — no home-grown schemes.",
       """You are an applied cryptographer. Use vetted primitives correctly:
authenticated encryption, correct nonce/IV handling, constant-time compares, KDFs
for passwords. Never invent a scheme. Flag any misuse you see."""),
]}


def registry_index() -> str:
    """A compact list of specialists for the system prompt."""
    lines = ["Specialist subagents you can delegate to with the `task` tool "
             "(each runs focused, then hands back a result):"]
    for s in REGISTRY.values():
        ro = " [read-only]" if s.read_only else ""
        lines.append(f"- {s.name}{ro} — {s.description}")
    return "\n".join(lines)


# ── the `task` tool ────────────────────────────────────────────────────
class TaskTool(Tool):
    name = "task"
    description = ('delegate a focused job to a specialist subagent. '
                  '<tool name="task">{"agent":"security-auditor","prompt":'
                  '"audit auth.py for authz bugs"}</tool>')
    summary = ("Delegate a focused task to a specialist subagent (security, "
               "tests, refactor, debug, …). It runs on its own and returns a result.")
    params = {
        "agent": {"type": "string", "description": "specialist name (see the list)"},
        "prompt": {"type": "string", "description": "the task, with all context it needs"},
    }
    required = ("agent", "prompt")

    def __init__(self, spawn: Callable[[Specialist, str, ToolContext], str]):
        # spawn(specialist, prompt, ctx) -> result text. Provided by the parent
        # Agent so the subagent shares its client/provider/workspace.
        self._spawn = spawn

    def summarize(self, args):
        return f'task → {args.get("agent", "?")}'

    def run(self, args, ctx: ToolContext) -> ToolResult:
        name = (args.get("agent") or "").strip()
        prompt = (args.get("prompt") or "").strip()
        spec = REGISTRY.get(name)
        if spec is None:
            return ToolResult(False, summary="unknown specialist",
                              output=f"no specialist {name!r}. Available: "
                                     f"{', '.join(REGISTRY)}.")
        if not prompt:
            return ToolResult(False, output="task needs a prompt.")
        try:
            result = self._spawn(spec, prompt, ctx)
        except Exception as e:
            return ToolResult(False, summary="subagent failed",
                              output=f"the {name} subagent crashed: {e}")
        return ToolResult(True, summary=f"{name} finished",
                          output=result or "(the subagent returned nothing)")
