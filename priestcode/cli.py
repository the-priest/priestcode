"""cli.py — the command line.

  priest                     launch the full-screen agent in the current repo
  priest "fix the parser"    launch and send that first message
  priest -p "…"              headless one-shot (prints the transcript, exits)
  priest auth                choose a provider and store an API key
  priest models              list providers and models
  priest config             show the resolved configuration

Flags: --provider/-P, --model/-m, --theme, --yolo, --cwd, --resume.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from . import config as C
from . import providers as P
from . import session as S


def main(argv: Optional[list] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(
        prog="priest",
        description="Priest Code — a fast, transparent terminal coding agent.")
    ap.add_argument("message", nargs="*", help="an initial message to send")
    ap.add_argument("-p", "--print", dest="headless", metavar="PROMPT",
                    help="headless: run one request and print the result")
    ap.add_argument("-P", "--provider", help="provider id (deepseek|openrouter|openai)")
    ap.add_argument("-m", "--model", help="model id (overrides the default)")
    ap.add_argument("--theme", help="priest | opencode | mono")
    ap.add_argument("-a", "--agent", help="agent/mode: build | plan | <custom>")
    ap.add_argument("--plan", action="store_true",
                    help="shortcut for --agent plan (read-only)")
    ap.add_argument("--live", action="store_true",
                    help="with `models`: also fetch the provider's live catalog")
    ap.add_argument("--yolo", action="store_true",
                    help="auto-approve shell commands (still blocks catastrophic)")
    ap.add_argument("--cwd", help="workspace directory (default: current dir)")
    ap.add_argument("--resume", nargs="?", const="__latest__",
                    help="resume the last session, or a session id")
    ap.add_argument("-v", "--version", action="store_true")
    ap.add_argument("cmd", nargs="?", help=argparse.SUPPRESS)  # auth/models/config

    args = ap.parse_args(argv)

    if args.version:
        print(f"priest {__version__}")
        return 0

    if args.plan:
        args.agent = "plan"

    # subcommands land in message[0]
    first = (args.message[0] if args.message else None)
    if first in ("auth", "models", "config", "init", "agents"):
        return _subcommand(first, args)

    workspace = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    if not workspace.is_dir():
        print(f"not a directory: {workspace}")
        return 2

    cfg = C.load(workspace)      # global + project (priestcode.json) config
    if args.agent:
        cfg.agent = args.agent
    if args.provider:
        if args.provider not in P.CATALOG:
            print(f"unknown provider {args.provider!r}. "
                  f"Available: {', '.join(P.CATALOG)}")
            return 2
        cfg.provider = args.provider
        cfg.model = ""            # reset model to the new provider's default
    if args.model:
        cfg.model = args.model
    if args.theme:
        cfg.theme = args.theme
    if args.yolo:
        cfg.approval = "yolo"

    prov = cfg.provider_obj()
    if prov is None:
        print(f"unknown provider {cfg.provider!r}. Try: {', '.join(P.CATALOG)}")
        return 2

    if not cfg.has_key():
        print(f"No API key for {prov.label}.")
        print(f"  Get one: {prov.signup}")
        print("  Then run:  priest auth")
        return 2

    model = prov.model(cfg.model_id()) or prov.default_model()
    key = cfg.resolved_key()

    from .agent import Agent
    from . import agents as _agents
    from . import context as _context
    from . import permissions as _perm

    agent_pool = _agents.from_config(cfg.agents)
    agent_def = _agents.get(cfg.agent, agent_pool)
    perms = _perm.Ruleset.from_config(cfg.permissions)
    instr = _context.load_instructions(workspace, cfg.instructions)

    agent = Agent(cfg, prov, model, key, workspace, agent_def=agent_def,
                  permissions=perms, instructions=instr)

    # MCP servers declared in the project config become tools
    if cfg.mcp:
        try:
            from . import mcp as _mcp
            mtools = _mcp.load_servers(cfg.mcp, notice=lambda s: None)
            agent.add_tools(mtools)
        except Exception:
            pass

    # resume a prior session's messages
    if args.resume:
        sid = S.latest() if args.resume == "__latest__" else args.resume
        sess = S.load(sid) if sid else None
        if sess and sess.messages:
            # keep our fresh system prompt, replay the rest
            agent.messages = [agent.messages[0]] + [
                m for m in sess.messages if m.get("role") != "system"]
            print(f"resumed session {sess.id}: {sess.title}")

    initial = args.headless or (" ".join(args.message) if args.message else None)

    if args.headless:
        return _headless(agent, cfg, args.headless)

    return _tui(agent, cfg, initial)


def _tui(agent, cfg, initial: Optional[str]) -> int:
    try:
        from .tui.app import PriestApp
    except Exception as e:
        print(f"could not start the full-screen UI ({e}); "
              f"falling back to plain mode. Use -p for headless.")
        return _headless(agent, cfg, initial or "")
    app = PriestApp(agent, cfg.theme)
    if initial:
        # send the first message once the app is mounted
        def _kick():
            inp = app.query_one("#prompt")
            inp.value = initial
            from textual.widgets import Input
            app.on_input_submitted(Input.Submitted(inp, initial))
        app.call_after_refresh(_kick)
    app.run()
    return 0


def _headless(agent, cfg, prompt: str) -> int:
    from .render import PlainRenderer, auto_approver
    if not prompt:
        print("nothing to do (headless mode needs a prompt: priest -p '…')")
        return 2
    r = PlainRenderer(show_thinking=False)
    agent.send(prompt, r, auto_approver(cfg.approval))
    return 0


# ── subcommands ──────────────────────────────────────────────────────
def _subcommand(name: str, args) -> int:
    if name == "models":
        for pid, prov in P.CATALOG.items():
            mark = "  (default provider)" if pid == P.DEFAULT_PROVIDER else ""
            print(f"\n{prov.label}  [{pid}]{mark}")
            print(f"  key: {prov.signup}")
            for m in prov.models:
                tags = []
                if m.price:
                    tags.append(m.price)
                if m.thinking_off:
                    tags.append("tools-tuned")
                if m.reasoning_effort:
                    tags.append("reasoning-dial")
                print(f"    {m.id:44} {m.label:22} {' '.join(tags)}")
        # live catalog for the active/selected provider
        if getattr(args, "live", False):
            cfg = C.load()
            if args.provider:
                cfg.provider = args.provider
            prov = cfg.provider_obj()
            if not cfg.has_key():
                print(f"\n(--live needs a key for {prov.label}; run `priest auth`)")
                return 0
            from .client import Client
            print(f"\nLive from {prov.label}:")
            ids = Client(prov, cfg.base_url(), cfg.resolved_key()).list_models_live()
            if not ids:
                print("  (could not fetch — network or key issue)")
            for i in sorted(ids):
                print(f"    {i}")
        return 0

    if name == "agents":
        from . import agents as _agents
        cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
        pool = _agents.from_config(C.load(cwd).agents)
        print("agents (switch with -a/--agent, /agent, or the palette):")
        for n, a in pool.items():
            ro = " [read-only]" if a.tools is not None else ""
            print(f"  {n:10} {a.description}{ro}")
        return 0

    if name == "init":
        cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
        dest = cwd / "AGENTS.md"
        if dest.exists():
            print(f"{dest.name} already exists — leaving it as is.")
            return 0
        dest.write_text(_agents_md_template(cwd), "utf-8")
        print(f"wrote {dest.name}. Edit it to teach Priest Code your project's "
              "conventions — it is loaded into context automatically.")
        return 0

    if name == "config":
        cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
        cfg = C.load(cwd)
        print(f"config file : {C.config_path()}")
        if cfg.project_files:
            print(f"project cfg : {', '.join(cfg.project_files)}")
        print(f"agent       : {cfg.agent}")
        print(f"provider    : {cfg.provider}")
        print(f"model       : {cfg.model_id()}")
        print(f"approval    : {cfg.approval}")
        print(f"theme       : {cfg.theme}")
        print(f"max_tokens  : {cfg.max_tokens}")
        print(f"key present : {'yes' if cfg.has_key() else 'NO'}")
        return 0

    if name == "auth":
        print("Providers:")
        ids = list(P.CATALOG)
        for i, pid in enumerate(ids, 1):
            print(f"  {i}. {P.CATALOG[pid].label}  [{pid}]")
        try:
            sel = input("choose a provider [1]: ").strip() or "1"
        except EOFError:
            return 1
        try:
            pid = ids[int(sel) - 1]
        except Exception:
            pid = sel if sel in P.CATALOG else P.DEFAULT_PROVIDER
        prov = P.CATALOG[pid]
        print(f"\n{prov.label}")
        print(f"  get a key: {prov.signup}")
        try:
            key = input("paste your API key (blank to cancel): ").strip()
        except EOFError:
            return 1
        if not key:
            print("cancelled.")
            return 1
        cfg = C.set_key(pid, key)
        cfg.provider = pid
        cfg.model = ""
        C.save(cfg)
        print(f"saved. provider set to {prov.label}. run `priest` to start.")
        return 0

    return 2


def _agents_md_template(cwd: Path) -> str:
    """A starter AGENTS.md, seeded with a scan of the repo."""
    import os
    langs = {}
    ext_lang = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript",
                ".js": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java",
                ".rb": "Ruby", ".c": "C", ".cpp": "C++", ".sh": "Shell"}
    tests = build = ""
    top = []
    for entry in sorted(os.listdir(cwd))[:40]:
        if entry.startswith(".") and entry not in (".github",):
            continue
        top.append(entry + ("/" if (cwd / entry).is_dir() else ""))
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in
                   {".git", "node_modules", "__pycache__", ".venv", "venv",
                    "dist", "build"}]
        for f in files:
            e = os.path.splitext(f)[1]
            if e in ext_lang:
                langs[ext_lang[e]] = langs.get(ext_lang[e], 0) + 1
        if root != str(cwd) and root.count(os.sep) - str(cwd).count(os.sep) > 2:
            dirs[:] = []
    if (cwd / "pyproject.toml").exists() or (cwd / "setup.py").exists():
        tests = "python -m pytest"
    elif (cwd / "package.json").exists():
        tests, build = "npm test", "npm run build"
    elif (cwd / "Cargo.toml").exists():
        tests, build = "cargo test", "cargo build"
    elif (cwd / "go.mod").exists():
        tests, build = "go test ./...", "go build ./..."
    lang_line = ", ".join(f"{k} ({v})" for k, v in
                          sorted(langs.items(), key=lambda x: -x[1])) or "unknown"
    return f"""# {cwd.name}

<!-- This file is loaded into Priest Code's context automatically. Edit it to
     teach the agent your project's conventions. -->

## Overview
(Describe what this project is in a sentence or two.)

## Stack
Languages detected: {lang_line}

## Layout
{chr(10).join('- ' + t for t in top[:20])}

## Commands
- Test:  `{tests or '(add your test command)'}`
- Build: `{build or '(add your build command, if any)'}`

## Conventions
- (Coding style, naming, patterns the agent should follow.)
- (Anything it should NOT touch.)
"""
