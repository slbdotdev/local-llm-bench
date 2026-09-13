"""v7.6 -- the v7.5 comparison re-run on fox, with slbh's TOOL LAYER as the variable.

v7.5 measured pi against slbh on the same twenty slots and found verdict parity (20/20 each)
at about twice the cost on every column. This runner is v7.5's, moved to the Linux controller
and given one new field, so a sweep's rows say which slbh build produced them.

Arm A, `pi`        : pibench.run_pi, the same path v7 and v7.5 ran.
Arm C, `slbh_real` : slbh's own headless mode, driving the real runtime, the real seat agent
                     and the real tool set. SLBH_BIN names the binary; --label names its commit.

The leafloop pilot arm is gone. It existed only because slbh had no headless entry point on
2026-09-12; `slbh -p` has one, so there is nothing an approximation adds. Its rows stay in
results/v75/v75r1.json as pilot evidence.

Everything else is held equal BY CONSTRUCTION, not by intention:

  * the same twenty task slots, results/v7/authoring/suite/
  * the same model tag, whose context window is baked into the tag itself
  * the same thinking level, medium -- pi sends it as reasoning_effort, and slbh sends the
    same field from --effort
  * the same wall cap
  * THE SAME GRADER: this module imports pibench and calls its parse_score / parse_verdict
    on output produced by pibench's own run_tree invocation of the task's hidden test.py.
    Re-implementing the grader would have introduced a second variable.

WHY THE v7.5 ROWS ARE NOT THE BEFORE. The v7.5 arm C ran the windows/amd64 build, whose
quick_bash is cmd.exe; 54% of its shell calls failed on `pwd`, `ls` and POSIX quoting. On
Linux shell_linux.go runs bash and that whole failure class is gone, so both arms are
re-measured here on fox before any tool change is made.

Environment this runner expects on fox (none of it is written here, so a row can never
silently run against the wrong endpoint):

  SLBH_HOME=~/work/v76-home                                    slbh's config and transcripts
  PIBENCH_OLLAMA=http://fractal.wyvern-temperature.ts.net:11434
  PIBENCH_NODE_BIN=/usr/bin
  PIBENCH_NODE_EXE=/usr/bin/node                    pibench's default appends node.exe
  PIBENCH_PI_CLI=~/.local/lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js
  --agent-dir .../ollama-bench/pi-agent-fox         the fox copy of the pi agent directory

Usage:
  python3 run76.py --arms pi --trials 1 --tag v76base-pi --model q27-IQ2_M-64k \
      --agent-dir ../../pi-agent-fox --label pi-0.85.1
  python3 run76.py --arms slbh_real --trials 1 --tag v76base-slbh --label d4b3930
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BENCH)
import pibench  # noqa: E402  -- the point is to reuse its grader, not copy it

SUITE = os.path.join(BENCH, "results", "v7", "authoring", "suite")
# Arm C runs under whichever interpreter drives the suite, so the binary must match the OS.
# It is built from the work clone and kept out of git:
#   cd ~/work/slbh-tools && GOTOOLCHAIN=auto go build -o results/v76/slbh-v76 ./cmd/slbh
_SLBH_DEFAULT = os.path.join(HERE, "slbh-v76.exe" if os.name == "nt" else "slbh-v76")
SLBH_BIN = os.environ.get("SLBH_BIN", _SLBH_DEFAULT)


def grade(sandbox, test_py):
    """pibench's grading block, verbatim in behaviour: hidden test copied in only now."""
    shutil.copy(test_py, os.path.join(sandbox, "_hidden_test.py"))
    gso, gse, grc, gto = pibench.run_tree(
        [sys.executable, "_hidden_test.py"], 60, cwd=sandbox,
        env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
        encoding="utf-8", errors="replace")
    if gto:
        return "grader timeout", False, None, None
    gout = (gso + gse)[-600:]
    return gout.strip(), (grc == 0 and "PASS" in gso), pibench.parse_score(gso), pibench.parse_verdict(gso)


def run_slbh_real(slot_dir, model, think, wall_s):
    """Arm C: slbh's own headless mode against the real runtime."""
    sandbox = tempfile.mkdtemp(prefix="v76c_")
    seed = os.path.join(slot_dir, "seed")
    if os.path.isdir(seed):
        shutil.copytree(seed, sandbox, dirs_exist_ok=True)
    prompt_file = os.path.join(slot_dir, "prompt.md")
    # slbh routes a model to its local Ollama provider by the `local/` prefix and strips it
    # on the wire, so the bare Ollama tag pi uses becomes `local/<tag>` here. Same model,
    # two spellings; a bare tag would fall through to OpenRouter and fail with no key.
    if not model.startswith("local/"):
        model = "local/" + model
    cmd = [SLBH_BIN, "--prompt-file", prompt_file, "--workdir", sandbox,
           "--model", model, "--timeout", f"{int(wall_s)}s", "--quiet"]
    if think:
        cmd += ["--effort", think]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    wall = time.time() - t0
    meta = {}
    try:
        meta = json.loads((p.stdout or "").strip().splitlines()[-1])
    except Exception:
        pass
    return sandbox, wall, p.returncode, meta, (p.stderr or "")[-400:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="pi,slbh_real")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--tag", default="v76r1")
    ap.add_argument("--model", default="q27-IQ2_M-64k")
    ap.add_argument("--think", default="medium")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--num-ctx", type=int, default=65536)
    ap.add_argument("--api", default="openai", choices=("openai", "native"))
    ap.add_argument("--endpoint", default=os.environ.get(
        "PIBENCH_OLLAMA", "http://fractal.wyvern-temperature.ts.net:11434"))
    ap.add_argument("--agent-dir", default="")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--suite", default=SUITE)
    # --label is the one field v7.5's runner did not have. Every row carries it, so a result
    # file that accumulates several sweeps still says which build produced each row; without
    # it the only evidence of which binary ran is the file name, which is not in the data.
    ap.add_argument("--label", default="", help="build identity for these rows, e.g. an slbh commit")
    ap.add_argument("--offset", type=int, default=0,
                    help="trial numbers start here, so a second trial appends instead of skipping")
    a = ap.parse_args()

    names = [t for t in a.tasks.split(",") if t] or sorted(os.listdir(a.suite))
    out_path = os.path.join(HERE, a.tag + ".json")
    data = json.load(open(out_path)) if os.path.exists(out_path) else {}
    data.setdefault("model", a.model)
    data.setdefault("rows", [])
    done = {(r["arm"], r["task"], r["trial"], r.get("label", "")) for r in data["rows"]}

    tasks = pibench.load_tasks(names, tasks_dir=a.suite)
    print(f"{len(tasks)} slots, arms={a.arms}, trials={a.trials}, model={a.model}, "
          f"label={a.label!r}, bin={SLBH_BIN}", flush=True)

    for arm in a.arms.split(","):
        for task in tasks:
            for trial in range(a.offset, a.offset + a.trials):
                key = (arm, task["name"], trial, a.label)
                if key in done:
                    print(f"  skip {arm}/{task['name']}/{trial} (already recorded)", flush=True)
                    continue
                t0 = time.time()
                if arm == "pi":
                    res = pibench.run_pi(a.model, task, a.think, a.timeout,
                                         agent_dir=a.agent_dir or pibench.AGENT_DIR)
                    row = {"arm": arm, "task": task["name"], "trial": trial,
                           "verdict": res.get("verdict"), "pass": res.get("pass"),
                           "score": res.get("score"), "wall_s": res.get("wall_s"),
                           "turns": res.get("turns"), "tool_calls": res.get("tool_calls"),
                           "in_tokens": res.get("in_tokens"), "out_tokens": res.get("out_tokens"),
                           "stop_reason": res.get("stop_reason"), "rc": res.get("rc"),
                           "errors": res.get("errors"), "grader": res.get("grader"),
                           "tools": res.get("tools")}
                elif arm == "slbh_real":
                    sandbox, wall, rc, meta, err = run_slbh_real(
                        os.path.join(a.suite, task["name"]), a.model, a.think, a.timeout)
                    gout, passed, score, verdict = grade(sandbox, task["test"])
                    row = {"arm": arm, "task": task["name"], "trial": trial,
                           "verdict": verdict, "pass": passed, "score": score,
                           "wall_s": round(wall, 1),
                           "turns": meta.get("turns"), "tool_calls": meta.get("tool_calls"),
                           "in_tokens": meta.get("prompt_tokens"),
                           "out_tokens": meta.get("output_tokens"),
                           "stop_reason": meta.get("stop_reason"), "rc": rc,
                           "errors": [err] if err else [], "grader": gout,
                           "sandbox": sandbox,
                           # slbh persists the full event record itself; the summary names it.
                           "runtime": meta.get("runtime"), "transcript": meta.get("transcript")}
                else:
                    sys.exit(f"unknown arm {arm!r}: this runner has pi and slbh_real only")
                row["label"] = a.label
                row["elapsed_s"] = round(time.time() - t0, 1)
                data["rows"].append(row)
                with open(out_path, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=1)
                print(f"  {arm}/{task['name']}/{trial}: {row['verdict']} "
                      f"score={row['score']} wall={row['wall_s']}s turns={row['turns']} "
                      f"tool_calls={row['tool_calls']}", flush=True)

    # tally
    print("\n=== tally ===", flush=True)
    for arm in a.arms.split(","):
        rows = [r for r in data["rows"] if r["arm"] == arm and r.get("label", "") == a.label]
        if not rows:
            continue
        ok = sum(1 for r in rows if r["verdict"] == "correct")
        print(f"{arm} [{a.label}]: {ok}/{len(rows)} correct", flush=True)
        from collections import Counter
        print("   verdicts:", dict(Counter(r["verdict"] for r in rows)), flush=True)
        for col in ("wall_s", "tool_calls", "turns", "out_tokens"):
            vals = [r[col] for r in rows if r.get(col) is not None]
            print(f"   {col}: {sum(vals):,.0f} over {len(vals)} rows", flush=True)


if __name__ == "__main__":
    main()
