"""Benchmark local Ollama models through the pi coding agent.

Usage: python pibench.py [--models a,b,c] [--tasks x,y] [--trials N] [--think off|low|medium|high]
       [--timeout SECS] [--tag NAME] [--no-tps] [--pad-tokens N]

For each model: measure raw Ollama TPS, then run every task `trials` times
through `pi -p --mode json` in a fresh sandbox, and grade with a hidden test.py
that is copied in only after pi has exited. Results land in results/<tag>.json
and results/<tag>.md.
"""
import threading, argparse
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(HERE, "tasks")  # overridden by --tasks-dir
AGENT_DIR = os.path.join(HERE, "pi-agent")
OLLAMA = "http://localhost:11434"
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
NODE_BIN = os.path.expanduser("~/scoop/apps/nodejs-lts/current")
# Call node + cli.js directly: launching pi.cmd goes through cmd.exe, which truncates
# argv at the first newline, so multi-line prompts would arrive as their first line only.
NODE_EXE = os.path.join(NODE_BIN, "node.exe")
PI_CLI = os.path.expanduser("~/scoop/persist/nodejs-lts/bin/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js")


def post(path, body, timeout=900):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def unload(model):
    try:
        post("/api/generate", {"model": model, "keep_alive": 0})
    except Exception:
        pass


def gpu_split(model):
    """Return (size_bytes, vram_bytes, pct_gpu) from /api/ps for a loaded model."""
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=10) as r:
            ps = json.load(r)
        for m in ps.get("models", []):
            if m["name"].split(":")[0] == model or m["model"] == model:
                size, vram = m["size"], m.get("size_vram", 0)
                return size, vram, round(100 * vram / size) if size else 0
    except Exception:
        pass
    return None, None, None


TPS_PROMPTS = [
    "Explain how a compiler turns source code into machine code, phase by phase, in detail.",
    "Describe TCP congestion control (slow start, congestion avoidance, fast retransmit) in detail.",
]


def tps(model, num_ctx):
    unload(model)
    t0 = time.time()
    post("/api/generate", {"model": model, "prompt": "hi", "stream": False, "think": False,
                           "options": {"num_predict": 8, "num_ctx": num_ctx}})
    load_s = time.time() - t0
    size, vram, pct = gpu_split(model)
    gen, prompt = [], []
    for p in TPS_PROMPTS:
        r = post("/api/generate", {"model": model, "prompt": p, "stream": False, "think": False,
                                   "options": {"num_predict": 400, "temperature": 0.2, "num_ctx": num_ctx}})
        gen.append(r["eval_count"] / (r["eval_duration"] / 1e9))
        prompt.append(r["prompt_eval_count"] / max(r["prompt_eval_duration"], 1) * 1e9)
    return {"gen_tps": round(statistics.mean(gen), 1), "prompt_tps": round(statistics.mean(prompt), 1),
            "load_s": round(load_s, 1), "size_gb": round((size or 0) / 2**30, 2),
            "vram_gb": round((vram or 0) / 2**30, 2), "pct_gpu": pct,
            "curve": tps_curve(model, num_ctx)}


FILLER = ("The quick brown fox jumps over the lazy dog while the committee reviews quarterly "
          "logistics reports, weather patterns, and the migration of monarch butterflies. ")


def tps_curve(model, num_ctx, fills=(0, 4096, 8192, 14000, 20000, 27000)):
    """Generation and prompt throughput as a function of how full the context is."""
    out = []
    for fill in fills:
        if fill + 512 > num_ctx:
            continue
        # ~5.95 chars per token for this filler (measured); Ollama reports the real count.
        text = (FILLER * (fill * 6 // len(FILLER) + 1))[: int(fill * 5.95)] if fill else ""
        prompt = f"Session {fill}. " + (text + "\n\n" if text else "") + "Write a detailed 300 word explanation of how hash tables work."
        r = post("/api/generate", {"model": model, "prompt": prompt, "stream": False, "think": False,
                                   "options": {"num_predict": 200, "temperature": 0.2, "num_ctx": num_ctx}})
        out.append({"fill_tokens": r["prompt_eval_count"],
                    "prompt_tps": round(r["prompt_eval_count"] / max(r["prompt_eval_duration"], 1) * 1e9, 1),
                    "gen_tps": round(r["eval_count"] / (r["eval_duration"] / 1e9), 1)})
        print(f"    ctx fill {r['prompt_eval_count']:6d} tok: prompt {out[-1]['prompt_tps']:7.1f} tok/s, gen {out[-1]['gen_tps']:5.1f} tok/s", flush=True)
    return out


def load_tasks(names=None, tasks_dir=None):
    tasks = []
    tasks_dir = tasks_dir or TASKS_DIR
    for name in sorted(os.listdir(tasks_dir)):
        d = os.path.join(tasks_dir, name)
        if not os.path.isdir(d) or name in ("ref",) or (names and name not in names):
            continue
        with open(os.path.join(d, "prompt.md"), encoding="utf-8") as f:
            prompt = f.read().strip()
        tasks.append({"name": name, "dir": d, "prompt": prompt,
                      "seed": os.path.join(d, "seed") if os.path.isdir(os.path.join(d, "seed")) else None,
                      "test": os.path.join(d, "test.py")})
    return tasks


SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)


def parse_score(text):
    """Optional partial credit: a grader may print `SCORE <n>/<m>` before its PASS/FAIL line."""
    m = None
    for m in SCORE_RE.finditer(text or ""):
        pass
    if not m:
        return None
    n, d = float(m.group(1)), float(m.group(2))
    return round(n / d, 4) if d else None


def parse_verdict(text):
    """Return the last `VERDICT <word>` line, or None when the grader omitted it."""
    verdict = None
    for m in VERDICT_RE.finditer(text or ""):
        verdict = m.group(1)
    return verdict


# 5.95 chars/token follows the measured filler used by tps_curve(), keeping the
# sandbox pad estimate consistent with the harness's existing context-fill precedent.
PAD_CHARS_PER_TOKEN = 5.95
PAD_RANDOM_SEED = 0x504942454E4348
# Filler must not be excludable by name or location. An agent that can glob the padding
# away is left with the unpadded sandbox, so the context axis silently measures nothing.
# Padding is therefore named like real material and placed in the same directories the seed
# uses; the manifest in the returned info (and padding.json) is what identifies it.
PAD_PY_STEMS = (
    "session_store", "retry_policy", "config_loader", "event_router", "cache_layer",
    "batch_worker", "schema_guard", "audit_trail", "rate_limiter", "token_bucket",
    "queue_adapter", "metrics_sink", "path_resolver", "field_mapper", "state_machine",
    "lease_manager", "backoff_timer", "record_codec", "index_builder", "shard_picker",
    "health_probe", "dep_resolver", "text_normalizer", "job_scheduler", "blob_writer",
)
PAD_MD_STEMS = (
    "runbook-cache", "design-notes", "review-2031-04", "ownership", "rollout-plan",
    "capacity-review", "incident-notes", "glossary", "interfaces", "retention-policy",
    "escalation-matrix", "onboarding", "dependencies", "known-issues", "changelog-archive",
    "naming-conventions", "data-contracts", "backfill-notes", "alerting", "postmortem-2031-02",
)
# Never shadow a task deliverable, whatever the seed happens to contain.
PAD_RESERVED_NAMES = frozenset({
    "solution.py", "answer.txt", "answer.json", "reference_audit.txt", "test.py",
    "padding.json", "results.json",
})

_PAD_PY_NAMES = (
    "archive_window", "cache_policy", "column_map", "dispatch_plan", "event_cursor",
    "feature_flags", "graph_index", "handoff_state", "item_digest", "job_limits",
    "key_schedule", "label_rules", "merge_queue", "node_snapshot", "offset_table",
    "partition_map", "query_shape", "retry_budget", "schema_notes", "transport_frame",
)
_PAD_MD_TOPICS = (
    "retention windows", "batch boundaries", "cache invalidation", "event ordering",
    "schema migration", "queue fairness", "failure recovery", "audit records",
    "configuration review", "service ownership", "release notes", "data contracts",
)
_PAD_MD_SENTENCES = (
    "The review should distinguish a missing observation from an observation that arrived late.",
    "A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.",
    "Operators usually need the reason for a decision as well as the final state of the record.",
    "The boundary is deliberately boring because predictable boundaries are easier to test.",
    "When the input is incomplete, preserve the uncertainty instead of manufacturing a default.",
    "The written procedure is also a compact record of which assumptions were in force.",
)


def _sandbox_material_chars(sandbox):
    total = 0
    for root, _, files in os.walk(sandbox):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total


def _pad_extension(sandbox):
    counts = {}
    for root, _, files in os.walk(sandbox):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext:
                counts[ext] = counts.get(ext, 0) + 1
    if not counts:
        return ".md"
    # Stable tie-breaking makes a repeated run deterministic even across filesystems.
    return sorted(counts, key=lambda ext: (-counts[ext], ext))[0]


def _seed_dir_shape(sandbox):
    """Relative directories holding real material, repeated by file count.

    Padding is drawn from this so filler lands where the seed already keeps material
    instead of piling up at the root, which is itself a give-away.
    """
    shape = []
    for root, dirs, files in os.walk(sandbox):
        # Never treat build/cache/VCS directories as real material: filler written into
        # __pycache__ is as good a marker as a filler-shaped filename would be.
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        real = [f for f in files if not f.startswith(".") and not f.endswith(".pyc")]
        if not real:
            continue
        rel = os.path.relpath(root, sandbox)
        rel = "" if rel == "." else rel
        if rel.startswith(".") or "__pycache__" in rel.split(os.sep):
            continue
        shape.extend([rel] * len(real))
    return shape or [""]


def _pad_filename(rng, extension, used):
    """A plausible name for real material, never a reserved deliverable name."""
    stems = PAD_PY_STEMS if extension == ".py" else PAD_MD_STEMS
    for _ in range(200):
        stem = rng.choice(stems)
        if rng.randrange(3) == 0:
            stem = f"{stem}_{rng.randrange(2, 9)}" if extension == ".py" else f"{stem}-{rng.randrange(2, 9)}"
        name = stem + extension
        if name not in used and name not in PAD_RESERVED_NAMES:
            return name
    # Deterministic fallback; still plausible, still not a marker.
    i = 0
    while True:
        name = f"module_{i:03d}{extension}" if extension == ".py" else f"note-{i:03d}{extension}"
        if name not in used and name not in PAD_RESERVED_NAMES:
            return name
        i += 1


def _pad_content(rng, extension, index, target_chars):
    """Build varied, plausible source/document material and trim it to the chunk size."""
    if extension == ".py":
        lines = [
            '"""Support module for an internal workflow review."""',
            "from dataclasses import dataclass",
            "from typing import Iterable",
            "",
            "@dataclass(frozen=True)",
            "class Record:",
            "    key: str",
            "    value: str",
            "    revision: int = 0",
            "",
        ]
        while sum(len(line) + 1 for line in lines) < target_chars + 300:
            name = rng.choice(_PAD_PY_NAMES) + "_" + str(rng.randrange(10, 99))
            topic = rng.choice(_PAD_MD_TOPICS)
            limit = rng.randrange(3, 18)
            lines.extend([
                f"def {name}(records: Iterable[Record], limit: int = {limit}) -> list[Record]:",
                f'    """Keep records relevant to {topic}; preserve input order."""',
                "    selected = []",
                "    for record in records:",
                "        if record.key and record.value:",
                "            selected.append(record)",
                "        if len(selected) >= limit:",
                "            break",
                "    return selected",
                "",
                f"# Review note {index}: {rng.choice(_PAD_MD_SENTENCES)}",
                "",
            ])
        text = "\n".join(lines) + "\n"
    else:
        headings = ("Purpose", "Inputs", "Operational notes", "Failure modes", "Open questions")
        lines = [f"# Internal note {index:04d}: {rng.choice(_PAD_MD_TOPICS).title()}", ""]
        while sum(len(line) + 1 for line in lines) < target_chars + 400:
            heading = rng.choice(headings)
            topic = rng.choice(_PAD_MD_TOPICS)
            lines.extend([
                f"## {heading}",
                "",
                f"This note records a deliberately narrow decision about {topic}. "
                f"The surrounding service may change, but the decision should remain easy to audit.",
                "",
                f"- Check the {topic} before changing the default behavior.",
                f"- Keep the owner and the review date next to the {heading.lower()} entry.",
                f"- {rng.choice(_PAD_MD_SENTENCES)}",
                "",
            ])
        text = "\n".join(lines) + "\n"
    return text[:target_chars]


def pad_sandbox(sandbox, pad_tokens):
    """Pad sandbox material to approximately ``pad_tokens`` estimated tokens.

    The estimate includes files already copied from seed/; only newly written files
    are reported in pad_chars_written and pad_files_written. ``pad_files`` is the
    manifest of written paths, relative to the sandbox: padding is identified by this
    list, never by its filenames, because a recognisable name lets a model exclude the
    fill and turn a 64k cell back into the unpadded one.

    NOTE: characters on disk are not context fill. Filler only enters the context if the
    model reads it, so the achieved fill of a trial must be taken from the model's own
    reported prompt token count, never from these numbers.
    """
    info = {"pad_tokens_requested": pad_tokens, "pad_files_written": 0,
            "pad_chars_written": 0, "pad_files": []}
    if not pad_tokens or pad_tokens < 0:
        return info
    target_chars = int(pad_tokens * PAD_CHARS_PER_TOKEN)
    remaining = max(0, target_chars - _sandbox_material_chars(sandbox))
    if not remaining:
        return info

    extension = _pad_extension(sandbox)
    rng = random.Random(PAD_RANDOM_SEED)
    shape = _seed_dir_shape(sandbox)
    used = set()
    for root, _, files in os.walk(sandbox):
        used.update(files)
    index = 0
    while remaining > 0:
        # Several medium-sized files make the filler look like a small source tree.
        chunk_chars = min(12000, max(1200, remaining // 8))
        content = _pad_content(rng, extension, index, chunk_chars)
        subdir = rng.choice(shape)
        filename = _pad_filename(rng, extension, used)
        target_dir = os.path.join(sandbox, subdir) if subdir else sandbox
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        try:
            with open(path, "x", encoding="utf-8", newline="") as f:
                f.write(content)
        except FileExistsError:
            # Exclusive creation protects seed material even if a name appears meanwhile.
            used.add(filename)
            index += 1
            continue
        used.add(filename)
        rel = os.path.relpath(path, sandbox).replace(os.sep, "/")
        info["pad_files"].append(rel)
        info["pad_files_written"] += 1
        info["pad_chars_written"] += len(content)
        remaining = max(0, target_chars - _sandbox_material_chars(sandbox))
        index += 1
    return info


class _NvidiaSmiSampler:
    """Best-effort daemon sampler; a broken probe must never affect a trial."""
    def __init__(self, interval=0.5):
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = None
        self.peak_mib = None

    def _sample(self):
        try:
            p = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2,
            )
            values = [int(line.strip().split()[0]) for line in p.stdout.splitlines() if line.strip()]
            if values:
                self.peak_mib = max(self.peak_mib or 0, max(values))
        except FileNotFoundError:
            self.stop_event.set()
        except Exception:
            pass

    def _run(self):
        self._sample()
        while not self.stop_event.wait(self.interval):
            self._sample()

    def start(self):
        try:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
        except Exception:
            self.thread = None

    def stop(self):
        self.stop_event.set()
        if self.thread:
            try:
                self.thread.join(timeout=0.25)
            except Exception:
                pass


MEM_GUARD_PROC_MB = 8192    # kill the tree if any single descendant exceeds this working set
MEM_GUARD_TREE_MB = 20480   # or the whole tree does
MEM_GUARD_PERIOD = 15       # seconds between polls


def _tree_mem_mb(root_pid):
    """(max single process MB, total MB) over root_pid and all descendants. Windows only; (0,0) elsewhere."""
    if os.name != "nt":
        return 0, 0
    ps = ("$m=@{}; Get-CimInstance Win32_Process | % { $m[[string]$_.ProcessId]=$_ }; "
          "$q=New-Object System.Collections.Queue; $q.Enqueue('ROOTPID'); $mx=0; $tot=0; "
          "while($q.Count){ $id=$q.Dequeue(); if($m[$id]){ $ws=[int]($m[$id].WorkingSetSize/1MB); "
          "$tot+=$ws; if($ws -gt $mx){$mx=$ws}; $m.Values | ? { [string]$_.ParentProcessId -eq $id } | % { $q.Enqueue([string]$_.ProcessId) } } }; "
          "\"$mx $tot\"").replace("ROOTPID", str(root_pid))
    try:
        r = subprocess.run(["pwsh", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30)
        a, b = r.stdout.split()
        return int(a), int(b)
    except Exception:
        return 0, 0


def _mem_guard(p):
    """Poll the child's process tree; kill it if a runaway grandchild (e.g. a model-written script)
    grows past the limits. A 31 GB and later a 19 GB python child were seen before this existed."""
    while p.poll() is None:
        time.sleep(MEM_GUARD_PERIOD)
        if p.poll() is not None:
            return
        mx, tot = _tree_mem_mb(p.pid)
        if mx > MEM_GUARD_PROC_MB or tot > MEM_GUARD_TREE_MB:
            p._mem_killed = "max %d MB / tree %d MB" % (mx, tot)
            print("[harness] MEMORY GUARD: killing tree pid %d (%s)" % (p.pid, p._mem_killed), flush=True)
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
            return


def run_tree(cmd, timeout, **kw):
    """subprocess.run-alike that kills the WHOLE process tree on timeout.
    subprocess.run only kills the direct child, so a hung grandchild (e.g. the model's own
    test script launched by pi's bash tool) would otherwise outlive the harness."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, **kw)
    guard = threading.Thread(target=_mem_guard, args=(p,), daemon=True)
    guard.start()
    try:
        out, err = p.communicate(timeout=timeout)
        if getattr(p, "_mem_killed", False):
            return (out or "") + "\n[harness] process tree killed by memory guard: " + p._mem_killed, err or "", -1, True
        return out, err, p.returncode, False
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        else:
            p.kill()
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return out or "", err or "", -1, True


def run_pi(model, task, think, timeout, provider="ollama", agent_dir=AGENT_DIR, pad_tokens=0):
    sandbox = tempfile.mkdtemp(prefix="pib_")
    if task["seed"]:
        shutil.copytree(task["seed"], sandbox, dirs_exist_ok=True)
    pad_info = pad_sandbox(sandbox, pad_tokens)
    env = dict(os.environ)
    env["PATH"] = NODE_BIN + os.pathsep + env["PATH"]
    if agent_dir:
        env["PI_CODING_AGENT_DIR"] = agent_dir
    else:
        env.pop("PI_CODING_AGENT_DIR", None)
    env["PI_OFFLINE"] = "1"
    env["PI_SKIP_VERSION_CHECK"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [NODE_EXE, PI_CLI, "-p", "--no-session", "--no-context-files", "--no-extensions", "--no-skills",
           "--no-prompt-templates", "--mode", "json", "--model", f"{provider}/{model}",
           "--thinking", think, "--", task["prompt"]]
    smi_sampler = _NvidiaSmiSampler() if provider == "ollama" else None
    if smi_sampler:
        smi_sampler.start()
    t0 = time.time()
    timed_out = False
    out, err, rc, timed_out = run_tree(cmd, timeout, cwd=sandbox, env=env, encoding="utf-8", errors="replace")
    if timed_out:
        err = "timeout"
    wall = time.time() - t0

    # Parse the JSON event stream.
    usage_in = usage_out = 0
    turns = tool_calls = 0
    tools = {}
    errors = []
    final_text = ""
    stop_reason = None          # F3: last stopReason pi reported (stop|toolUse|length|error|aborted|...)
    stop_reasons = {}           # F3: histogram over all assistant messages in the run
    events = {}                 # F3: counts of compaction_end / auto_retry_end
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "message_end":
            msg = ev.get("message", {})
            if msg.get("role") == "assistant":
                turns += 1
                u = msg.get("usage") or {}
                usage_in += u.get("input", 0) + u.get("cacheRead", 0)
                usage_out += u.get("output", 0)
                sr = msg.get("stopReason")
                if sr:
                    stop_reason = sr
                    stop_reasons[sr] = stop_reasons.get(sr, 0) + 1
                if msg.get("stopReason") == "error" or msg.get("errorMessage"):
                    errors.append(str(msg.get("errorMessage"))[:200])
                for c in msg.get("content", []):
                    if c.get("type") == "text":
                        final_text = c.get("text", "")
        elif t == "tool_execution_start":
            tool_calls += 1
            tn = ev.get("toolName", "?")
            tools[tn] = tools.get(tn, 0) + 1
        elif t in ("compaction_end", "auto_retry_end"):
            events[t] = events.get(t, 0) + 1

    # Sample /api/ps before grading and before the model is unloaded. gpu_split is
    # deliberately best-effort, as residency data must never fail a trial.
    if provider == "ollama":
        try:
            ps_size, ps_vram, ps_pct = gpu_split(model)
        except Exception:
            ps_size, ps_vram, ps_pct = None, None, None
    else:
        ps_size, ps_vram, ps_pct = None, None, None

    # Grade: hidden test copied in only now.
    shutil.copy(task["test"], os.path.join(sandbox, "_hidden_test.py"))
    gso, gse, grc, gto = run_tree([sys.executable, "_hidden_test.py"], 60, cwd=sandbox,
                                  env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
                                  encoding="utf-8", errors="replace")
    verdict = None
    if gto:
        gout, passed, score = "grader timeout", False, None
    else:
        gout = (gso + gse)[-600:]
        passed = grc == 0 and "PASS" in gso
        score = parse_score(gso)
        verdict = parse_verdict(gso)

    if smi_sampler:
        smi_sampler.stop()

    # in_tokens is pi's achieved input-token usage, not pad_tokens_requested;
    # reports should quote it as the cell's actual context fill.
    result = {"task": task["name"], "pass": passed, "wall_s": round(wall, 1), "turns": turns,
              "tool_calls": tool_calls, "tools": tools, "in_tokens": usage_in, "out_tokens": usage_out,
              "timed_out": timed_out, "rc": rc, "errors": errors, "grader": gout.strip(), "score": score,
              "verdict": verdict, "pad_tokens_requested": pad_info["pad_tokens_requested"],
              "pad_files_written": pad_info["pad_files_written"],
              "pad_chars_written": pad_info["pad_chars_written"],
              "ps_size_gb": round(ps_size / 2**30, 2) if ps_size is not None else None,
              "ps_vram_gb": round(ps_vram / 2**30, 2) if ps_vram is not None else None,
              "ps_pct_gpu": ps_pct, "nvidia_smi_peak_mib": smi_sampler.peak_mib if smi_sampler else None,
              "final_text": final_text[-400:], "stderr": err[-400:].strip(),
              "stop_reason": stop_reason, "stop_reasons": stop_reasons, "events": events}
    # Diagnostics only: PIBENCH_KEEP=<dir> preserves each sandbox before deletion so a
    # malformed deliverable can be inspected byte-for-byte. Unset by default, so the
    # normal path is unchanged.
    keep_root = os.environ.get("PIBENCH_KEEP")
    if keep_root:
        try:
            dest = os.path.join(keep_root, "%s-trial%s-%s" % (
                task["name"], result.get("trial", "x"), os.path.basename(sandbox)))
            os.makedirs(keep_root, exist_ok=True)
            shutil.copytree(sandbox, dest, dirs_exist_ok=True)
        except Exception:
            pass
    shutil.rmtree(sandbox, ignore_errors=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="q27-Q3_K_M,q27-Q3_K_L,q27-Q3_K_S,q27-Q2_K_L")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--think", default="medium")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--num-ctx", type=int, default=32768)
    ap.add_argument("--tag", default="")
    ap.add_argument("--no-tps", action="store_true")
    ap.add_argument("--retps", action="store_true", help="re-measure TPS even if already recorded")
    ap.add_argument("--tasks-dir", default="", help="task directory (default: tasks/)")
    ap.add_argument("--agent-dir", default="", help="override PI_CODING_AGENT_DIR (default: bench pi-agent for ollama, managed ~/.pi/agent otherwise)")
    ap.add_argument("--provider", default="ollama", help="ollama (bench agent dir) or openrouter (managed ~/.pi/agent)")
    ap.add_argument("--pad-tokens", type=int, default=0, help="estimated total sandbox context material (0 disables padding)")
    a = ap.parse_args()
    models = a.models.split(",")
    tasks = load_tasks(a.tasks.split(",") if a.tasks else None, os.path.join(HERE, a.tasks_dir) if a.tasks_dir and not os.path.isabs(a.tasks_dir) else (a.tasks_dir or None))
    tag = a.tag or f"{a.provider}-think-{a.think}"
    agent_dir = a.agent_dir or (AGENT_DIR if a.provider == "ollama" else "")
    if a.provider != "ollama":
        a.no_tps = True
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out_json = os.path.join(HERE, "results", tag + ".json")
    results = {}
    if os.path.exists(out_json):
        with open(out_json, encoding="utf-8") as f:
            results = json.load(f)

    for model in models:
        print(f"\n===== {model} =====", flush=True)
        r = results.setdefault(model, {"tps": None, "runs": []})
        if not a.no_tps and (r["tps"] is None or a.retps):
            r["tps"] = tps(model, a.num_ctx)
            print("TPS:", r["tps"], flush=True)
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=1)
        done = {(x["task"], x["trial"]) for x in r["runs"]}
        for t in tasks:
            for trial in range(a.trials):
                if (t["name"], trial) in done:
                    continue
                res = run_pi(model, t, a.think, a.timeout, a.provider, agent_dir, a.pad_tokens)
                res["trial"] = trial
                r["runs"].append(res)
                print(f"  {t['name']:16s} #{trial} {'PASS' if res['pass'] else 'FAIL'} "
                      f"{res['wall_s']:6.1f}s turns={res['turns']} tools={res['tool_calls']} "
                      f"out={res['out_tokens']} VERDICT={res['verdict'] or '-'} STOP={res['stop_reason'] or '-'}"
                      + (" TIMEOUT" if res["timed_out"] else "")
                      + (f" ERR={res['errors'][0][:60]}" if res["errors"] else ""), flush=True)
                with open(out_json, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=1)
        if a.provider == "ollama":
            unload(model)

    # Summary table.
    lines = [f"# pi bench ({tag})", "", "| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run | correct | visibly_failed | confidently_wrong | confidently_wrong rate | length stops |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for model, r in results.items():
        runs = r["runs"]
        if not runs:
            continue
        n = len(runs)
        p = sum(x["pass"] for x in runs)
        tp = r["tps"] or {}
        per_task = {}
        for x in runs:
            per_task.setdefault(x["task"], []).append(x["pass"])
        solved = sum(1 for v in per_task.values() if all(v))
        curve = tp.get("curve") or []
        gen_str = f"{tp.get('gen_tps','?')}" + (f" / {curve[-1]['gen_tps']} @{curve[-1]['fill_tokens']}" if curve else "")
        n_len = sum(x.get("stop_reasons", {}).get("length", 0) for x in runs)
        n_len_runs = sum(1 for x in runs if x.get("stop_reasons", {}).get("length"))
        scored = [x["score"] for x in runs if x.get("score") is not None]
        score_str = f"{statistics.mean(scored):.2f} ({len(scored)}/{n} runs)" if scored else "-"
        verdict_counts = {v: sum(1 for x in runs if x.get("verdict") == v)
                          for v in ("correct", "visibly_failed", "confidently_wrong")}
        confident_rate = f"{verdict_counts['confidently_wrong'] / n:.1%}" if n else "-"
        lines.append(f"| {model} | {tp.get('size_gb','?')} GB | {tp.get('pct_gpu','?')} | {gen_str} | "
                     f"{p}/{n} | {score_str} | {solved}/{len(per_task)} all-trials | {statistics.mean(x['wall_s'] for x in runs):.0f}s | "
                     f"{statistics.mean(x['out_tokens'] for x in runs):.0f} | {statistics.mean(x['tool_calls'] for x in runs):.1f} | "
                     f"{verdict_counts['correct']} | {verdict_counts['visibly_failed']} | "
                     f"{verdict_counts['confidently_wrong']} | {confident_rate} | {n_len} in {n_len_runs}/{n} |")
    lines += ["", "## Per task (passes/trials)", "", "| task | " + " | ".join(results) + " |",
              "|---|" + "---|" * len(results)]
    for t in tasks:
        row = []
        for model, r in results.items():
            rs = [x for x in r["runs"] if x["task"] == t["name"]]
            v = [x["pass"] for x in rs]
            sc = [x["score"] for x in rs if x.get("score") is not None]
            cell = f"{sum(v)}/{len(v)}" + (f" (score {statistics.mean(sc):.2f})" if sc else "")
            row.append(cell if v else "-")
        lines.append(f"| {t['name']} | " + " | ".join(row) + " |")
    md = "\n".join(lines)
    with open(os.path.join(HERE, "results", tag + ".md"), "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print("\n" + md)


if __name__ == "__main__":
    main()
