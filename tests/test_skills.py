#!/usr/bin/env python3
"""test_skills.py — the skill library, the `skill` tool, and subagent delegation."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import skills as SK          # noqa: E402
from priestcode import subagents as SUB       # noqa: E402
from priestcode import tools as T             # noqa: E402
from priestcode import agent as A, config as C, providers as P  # noqa: E402
from priestcode import client as CL, events as E                # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


print("== the bundled library loads (300+ skills) ==")
sk = SK.load_skills()
ck("300+ skills bundled", len(sk) >= 300, str(len(sk)))
ck("every skill has a name+description",
   all(s.name and s.description for s in sk.values()))
ck("categories are populated",
   len({s.category for s in sk.values()}) >= 15,
   str(len({s.category for s in sk.values()})))
ck("security skills are present (the operator's field)",
   any(s.category.startswith("security") for s in sk.values()))
idx = SK.skills_index(sk)
ck("index is compact enough for the prompt (<12k chars)", len(idx) < 12000, str(len(idx)))
ck("index names the categories", "security" in idx)

print("\n== the skill tool: search / list / load ==")
ctx = T.ToolContext(cwd=Path(tempfile.mkdtemp()), approve=lambda *a: True,
                    approval_mode="yolo")
st = SK.SkillTool(sk)
r = st.run({"action": "search", "query": "sql injection"}, ctx)
ck("search finds SQL injection", r.ok and "SQL injection" in r.output, r.output[:80])
r = st.run({"action": "load", "name": "SQL injection"}, ctx)
ck("load returns the full body", r.ok and "## Checklist" in r.output)
ck("load is case-insensitive tolerant",
   st.run({"action": "load", "name": "sql injection"}, ctx).ok)
r = st.run({"action": "load", "name": "no-such-skill-xyz"}, ctx)
ck("unknown skill fails with suggestions", not r.ok and "search" in r.output)
r = st.run({"action": "list", "category": "security/web"}, ctx)
ck("list a category works", r.ok and "injection" in r.output.lower())

print("\n== frontmatter parsing ==")
one = SK._parse_skill(
    "---\nname: X\ndescription: d\ncategory: c\ntags: [a, b]\n---\n# X\nbody",
    "fallback")
ck("parses name/desc/category/tags",
   one.name == "X" and one.description == "d" and one.category == "c"
   and one.tags == ["a", "b"])
ck("no-frontmatter still yields a skill",
   SK._parse_skill("# Title\ntext", "fb").name == "Title")

print("\n== subagent registry ==")
ck("specialists registered (15+)", len(SUB.REGISTRY) >= 15, str(len(SUB.REGISTRY)))
ck("security-auditor is read-only", SUB.REGISTRY["security-auditor"].read_only)
ck("registry index lists them", "security-auditor" in SUB.registry_index())

print("\n== the agent wires skills + subagents in ==")
ws = Path(tempfile.mkdtemp())
cfg = C.Config(approval="yolo")
prov = P.get_provider("siliconflow")
ag = A.Agent(cfg, prov, prov.default_model(), "k", ws)
ck("skill tool registered", "skill" in ag.tools)
ck("task tool registered", "task" in ag.tools)
ck("system prompt carries the skills index", "# Skills" in ag.messages[0]["content"])
ck("system prompt carries the subagents index",
   "# Subagents" in ag.messages[0]["content"])

print("\n== a subagent runs headless and writes for real ==")
main_script = [
    CL.Completion(text="", finish_reason="tool_calls", tool_calls=[
        {"id": "t1", "name": "task",
         "arguments": json.dumps({"agent": "test-writer",
                                  "prompt": "make hello.py"})}]),
    CL.Completion(text="Delegated.", finish_reason="stop")]
sub_script = [
    CL.Completion(text="", finish_reason="tool_calls", tool_calls=[
        {"id": "w1", "name": "write_file",
         "arguments": json.dumps({"path": "hello.py", "content": "print(1)\n"})}]),
    CL.Completion(text="Wrote hello.py.", finish_reason="stop")]
state = {"main": 0, "sub": 0}


def fake_stream(self, model, messages, on_token, on_reasoning=None, **kw):
    if "# Agent: test-writer" in messages[0]["content"]:   # only the child
        i = state["sub"]; state["sub"] += 1
        c = sub_script[min(i, len(sub_script) - 1)]
    else:
        i = state["main"]; state["main"] += 1
        c = main_script[min(i, len(main_script) - 1)]
    if c.text:
        on_token(c.text)
    return c


_orig = CL.Client.stream
CL.Client.stream = fake_stream
try:
    ag2 = A.Agent(cfg, prov, prov.default_model(), "k", ws)
    evs = []
    ag2.send("delegate making hello.py", evs.append, lambda k, p, d: True)
finally:
    CL.Client.stream = _orig
ck("the task tool ran",
   any(isinstance(e, E.ToolFinished) and e.name == "task" for e in evs))
ck("the subagent actually wrote the file", (ws / "hello.py").is_file())
child = A.Agent(cfg, prov, prov.default_model(), "k", ws, enable_subagents=False)
ck("a subagent does NOT get the task tool (no unbounded recursion)",
   "task" not in child.tools)
ck("a subagent still gets the skill tool", "skill" in child.tools)

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
