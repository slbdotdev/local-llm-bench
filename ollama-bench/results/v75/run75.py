"""v7.5 -- the v7 suite with exactly one variable changed: the agent harness.

Arm A, `pi`   : pibench.run_pi, the same path v7 itself ran.
Arm B, `slbh` : results/v8/item1/leafloop.py, slbh's own system prompt and its nineteen tool
                schemas lifted verbatim from slbh's source and differentially tested against
                slbh's real harness.Runtime.ExecuteTool.

Everything else is held equal BY CONSTRUCTION, not by intention:

  * the same twenty task slots, results/v7/authoring/suite/
  * the same model tag, whose context window is baked into the tag itself
  * the same thinking level, medium -- pi sends it as reasoning_effort, and leafloop was
    given a --think flag that sends the same field on the same wire shape
  * the same wall cap
  * THE SAME GRADER: this module imports pibench and calls its parse_score / parse_verdict
    on output produced by pibench's own run_tree invocation of the task's hidden test.py.
    Re-implementing the grader would have introduced a second variable.

Both arms are measured NOW. Comparing arm B against v7's recorded 19/20 would confound the
harness with everything that has changed since: model tags, ollama version, config, date.

Usage:
  python run75.py --arms pi,slbh --trials 1 --tag v75r1 --model q27-IQ2_M-64k
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BENCH)
import pibench  # noqa: E402  -- the point is to reuse its grader, not copy it

SUITE = os.path.join(BENCH, "results", "v7", "authoring", "suite")
LEAFLOOP = os.path.join(BENCH, "results", "v8", "item1", "leafloop.py")


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


def run_slbh(slot_dir, model, endpoint, think, wall_s, num_ctx, api):
    sandbox = tempfile.mkdtemp(prefix="v75s_")
    shutil.rmtree(sandbox)                      # leafloop recreates it from the slot's seed/
    tx = tempfile.mkstemp(prefix="v75t_", suffix=".jsonl")[1]
    cmd = [sys.executable, LEAFLOOP,
           "--task", slot_dir, "--sandbox", sandbox, "--transcript", tx,
           "--endpoint", endpoint, "--api", api, "--model", model,
           "--wall-s", str(wall_s), "--no-inject"]
    if think:
        cmd += ["--think", think]
    if num_ctx:
        cmd += ["--num-ctx", str(num_ctx)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    wall = time.time() - t0
    # leafloop prints a JSON summary on stdout and writes a rec="trial" record last.
    meta = {}
    try:
        meta = json.loads((p.stdout or "").strip().splitlines()[-1])
    except Exception:
        try:
            for line in open(tx, encoding="utf-8"):
                rec = json.loads(line)
                if rec.get("rec") == "trial":
                    meta = rec
        except Exception:
            pass
    # tool_calls is not in the summary; count it from the transcript, best effort.
    ncalls = 0
    try:
        for line in open(tx, encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("rec") in ("tool_call", "tool_result"):
                ncalls += 1
    except Exception:
        ncalls = None
    if ncalls is not None:
        meta = dict(meta, tool_calls_counted=ncalls)
    return sandbox, wall, p.returncode, meta, tx, (p.stderr or "")[-400:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="pi,slbh")
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--tag", default="v75r1")
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
    a = ap.parse_args()

    names = [t for t in a.tasks.split(",") if t] or sorted(os.listdir(a.suite))
    out_path = os.path.join(HERE, a.tag + ".json")
    data = json.load(open(out_path)) if os.path.exists(out_path) else {}
    data.setdefault("model", a.model)
    data.setdefault("rows", [])
    done = {(r["arm"], r["task"], r["trial"]) for r in data["rows"]}

    tasks = pibench.load_tasks(names, tasks_dir=a.suite)
    print(f"{len(tasks)} slots, arms={a.arms}, trials={a.trials}, model={a.model}", flush=True)

    for arm in a.arms.split(","):
        for task in tasks:
            for trial in range(a.trials):
                key = (arm, task["name"], trial)
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
                           "errors": res.get("errors"), "grader": res.get("grader")}
                else:
                    sandbox, wall, rc, meta, tx, err = run_slbh(
                        os.path.join(a.suite, task["name"]), a.model, a.endpoint,
                        a.think, a.timeout, a.num_ctx, a.api)
                    gout, passed, score, verdict = grade(sandbox, task["test"])
                    row = {"arm": arm, "task": task["name"], "trial": trial,
                           "verdict": verdict, "pass": passed, "score": score,
                           "wall_s": round(wall, 1),
                           "turns": meta.get("turns"), "tool_calls": meta.get("tool_calls_counted"),
                           "in_tokens": meta.get("peak_prompt") or meta.get("prompt_tokens"),
                           "out_tokens": meta.get("output_tokens"),
                           "stop_reason": meta.get("stop_reason"), "rc": rc,
                           "errors": [err] if err else [], "grader": gout,
                           "transcript": tx, "sandbox": sandbox}
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
        rows = [r for r in data["rows"] if r["arm"] == arm]
        if not rows:
            continue
        ok = sum(1 for r in rows if r["verdict"] == "correct")
        print(f"{arm}: {ok}/{len(rows)} correct", flush=True)
        from collections import Counter
        print("   verdicts:", dict(Counter(r["verdict"] for r in rows)), flush=True)


if __name__ == "__main__":
    main()
