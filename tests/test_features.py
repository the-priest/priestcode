#!/usr/bin/env python3
"""test_features.py — the OpenCode-parity features: ambient instructions,
project config discovery, @-mentions, permissions, agents/modes, snapshots."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import context as CX, permissions as PM, agents as AG  # noqa
from priestcode import snapshots as SN, agent as A, client as CL  # noqa
from priestcode import config as C, providers as P  # noqa

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


# ── ambient instructions + project config discovery ─────────────────
print("== instructions + config discovery ==")
root = Path(tempfile.mkdtemp())
(root / "AGENTS.md").write_text("# Rules\nUse tabs, not spaces.\n")
sub = root / "src"
sub.mkdir()
(root / "priestcode.json").write_text(json.dumps({
    "model": "zai-org/GLM-5.3-Flash", "approval": "yolo",
    "permissions": [{"action": "bash", "resource": "rm *", "effect": "deny"}],
    "instructions": ["docs/*.md"]}))
(root / "docs").mkdir()
(root / "docs" / "style.md").write_text("Prefer small functions.")

instr = CX.load_instructions(root)
ck("AGENTS.md is picked up", "Use tabs" in instr, instr[:60])
merged, used = CX.find_project_config(sub)      # discovered from a subdir
ck("project config found from subdir", merged.get("approval") == "yolo", str(merged))
ck("project instructions glob resolves",
   "small functions" in CX.load_instructions(root, ["docs/*.md"]))

print("\n== config layering applies the project file ==")
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()
cfg = C.load(sub)
ck("project model overrides default",
   cfg.model == "zai-org/GLM-5.3-Flash", cfg.model)
ck("project approval applied", cfg.approval == "yolo")
ck("project permissions loaded", len(cfg.permissions) == 1)

print("\n== @-mentions expand to file contents ==")
(root / "target.py").write_text("SECRET = 42\n")
out = CX.expand_mentions("look at @target.py please", root)
ck("mention body inlined", "SECRET = 42" in out, out[:80])
ck("mention outside workspace not expanded (no file inlined)",
   "Referenced files:" not in CX.expand_mentions("@/etc/passwd", root))

# ── permissions ─────────────────────────────────────────────────────
print("\n== permissions ruleset ==")
rs = PM.Ruleset.from_config([
    {"action": "bash", "resource": "git *", "effect": "allow"},
    {"action": "bash", "resource": "*", "effect": "ask"},
    {"action": "edit", "resource": "*", "effect": "allow"}])
ck("git allowed", rs.evaluate("bash", "git status") == "allow")
ck("other bash asks", rs.evaluate("run", "npm test") == "ask")
ck("edit allowed", rs.evaluate("write_file", "a.py") == "allow")
ck("unknown action, no rule -> None",
   PM.Ruleset([]).evaluate("bash", "ls") is None)
deny = PM.Ruleset.from_config([{"action": "bash", "resource": "rm *",
                                "effect": "deny"}])
ck("deny matches", deny.evaluate("bash", "rm -rf x") == "deny")

# ── agents / modes ──────────────────────────────────────────────────
print("\n== agents / modes ==")
ck("build has all tools", AG.BUILTIN["build"].tools is None)
ck("plan is read-only (no write/run)",
   "write_file" not in AG.BUILTIN["plan"].toolset()
   and "run" not in AG.BUILTIN["plan"].toolset()
   and "read_file" in AG.BUILTIN["plan"].toolset())
custom = AG.from_config({"reviewer": {"tools": ["read_file", "grep"],
                                      "description": "reviews"}})
ck("custom agent from config", "reviewer" in custom
   and set(custom["reviewer"].toolset()) == {"read_file", "grep"})

# ── snapshots / undo ────────────────────────────────────────────────
print("\n== snapshots / undo ==")
st = SN.SnapshotStack()
f = root / "edit_me.txt"
f.write_text("v1")
st.push(f, "v1")           # before changing to v2
f.write_text("v2")
msg = st.undo()
ck("undo restores previous content", f.read_text() == "v1", f.read_text())
# undo a creation → removes the file
newf = root / "created.txt"
st.push(newf, None)
newf.write_text("hi")
st.undo()
ck("undo of a creation removes the file", not newf.exists())

# ── plan mode blocks writes end-to-end ──────────────────────────────
print("\n== plan mode refuses to write (end to end) ==")
ws = Path(tempfile.mkdtemp())
pcfg = C.Config(approval="yolo", agent="plan")
prov = P.get_provider("siliconflow")
ag = A.Agent(pcfg, prov, prov.default_model(), "k", ws,
             agent_def=AG.BUILTIN["plan"])
script = ['<tool name="write_file">{"path":"x.py","content":"nope"}</tool>',
          "I can only plan; switch me to build to write."]
stt = {"i": 0}


def fake(model, messages, on_token, on_reasoning=None, **kw):
    i = stt["i"]; stt["i"] += 1
    t = script[min(i, len(script) - 1)]
    on_token(t)
    return CL.Completion(text=t, finish_reason="stop")


ag.client.stream = fake
ag.send("write x.py", lambda e: None, lambda k, p, d: True)
ck("plan mode did NOT create the file", not (ws / "x.py").exists())
ck("plan mode has no write tool", "write_file" not in ag.tools)

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
