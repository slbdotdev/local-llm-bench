"""Independently verify every authored v5 candidate. No model, no GPU, no network.

This is plan section 6 loop step 2 (the mechanical selfcheck) plus an audit of the three
claims each authoring worker made about its own checker. A worker's report is a claim; this
recomputes it.

For each tasks-v5/<id>/cand-N/ it builds two sandboxes exactly the way pibench.py does --
seed/ copied in, then the hidden checker copied in as _hidden_test.py and run with cwd set
to the sandbox, PYTHONUTF8=1, under a 60 s timeout -- and asserts:

  REF sandbox    seed/ + ref/   ->  rc 0, "PASS", SCORE m/m, VERDICT correct
  EMPTY sandbox  seed/ only     ->  rc nonzero, VERDICT visibly_failed, and NOT a crash
                                    of the grader itself

The empty case is the one worth having. A checker that raises instead of reporting turns a
model that produced nothing into an unscored trial, and across 120 grid trials that silently
eats the denominator of the headline rate.

Run with WINDOWS python so it matches the harness that will really run these:
  /mnt/c/Users/slb/scoop/apps/python/current/python.exe verify_candidates.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "tasks-v5"))
SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)


def run_checker(cand, with_ref):
    sandbox = tempfile.mkdtemp(prefix="v5v_")
    try:
        seed = os.path.join(cand, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sandbox, dirs_exist_ok=True)
        if with_ref:
            ref = os.path.join(cand, "ref")
            if os.path.isdir(ref):
                shutil.copytree(ref, sandbox, dirs_exist_ok=True)
            # Two ref conventions exist in this suite and both are legitimate: most tasks
            # ship the finished artifact (a module the checker imports, or an answer file),
            # while t01 ships solve.py, a program that PRODUCES the artifact. Run it, or the
            # reference looks like a total failure and the task looks broken when it is not.
            solve = os.path.join(sandbox, "solve.py")
            if os.path.isfile(solve):
                subprocess.run([sys.executable, "solve.py"], cwd=sandbox,
                               env=dict(os.environ, PYTHONUTF8="1"),
                               capture_output=True, timeout=60)
                os.remove(solve)
        test = os.path.join(cand, "test.py")
        if not os.path.isfile(test):
            return {"error": "no test.py"}
        shutil.copy(test, os.path.join(sandbox, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            out, err, rc, to = p.stdout, p.stderr, p.returncode, False
        except subprocess.TimeoutExpired:
            out, err, rc, to = "", "grader timeout", -1, True
        sc = SCORE_RE.findall(out)
        vd = VERDICT_RE.findall(out)
        return {"rc": rc, "timeout": to, "pass": (rc == 0 and "PASS" in out),
                "score": (float(sc[-1][0]), float(sc[-1][1])) if sc else None,
                "verdict": vd[-1] if vd else None,
                # a traceback on stderr means the grader itself broke, which is different
                # from the candidate failing and must never be reported as a model result
                "grader_crashed": "Traceback" in err,
                "stderr_tail": err.strip()[-200:]}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    rows, problems = [], []
    for tid in sorted(os.listdir(TASKS)):
        tdir = os.path.join(TASKS, tid)
        if not os.path.isdir(tdir):
            continue
        for cn in sorted(os.listdir(tdir)):
            cand = os.path.join(tdir, cn)
            if not os.path.isdir(cand) or not cn.startswith("cand-"):
                continue
            name = f"{tid}/{cn}"
            prompt = os.path.join(cand, "prompt.md")
            pw = len(open(prompt, encoding="utf-8").read().split()) if os.path.isfile(prompt) else 0
            seed_files = []
            sd = os.path.join(cand, "seed")
            if os.path.isdir(sd):
                for root, _, fs in os.walk(sd):
                    seed_files += [os.path.join(root, f) for f in fs]
            seed_bytes = sum(os.path.getsize(f) for f in seed_files)

            r = run_checker(cand, with_ref=True)
            e = run_checker(cand, with_ref=False)
            ok_ref = (not r.get("error") and r.get("pass") and r.get("verdict") == "correct"
                      and r.get("score") and r["score"][0] == r["score"][1])
            ok_empty = (not e.get("error") and not e.get("pass")
                        and e.get("verdict") == "visibly_failed"
                        and not e.get("grader_crashed"))
            rows.append({"cand": name, "prompt_words": pw, "seed_files": len(seed_files),
                         "seed_kb": round(seed_bytes / 1024, 1),
                         "ref": r, "empty": e, "ok_ref": ok_ref, "ok_empty": ok_empty})
            if not os.path.isfile(prompt):
                problems.append(f"{name}: no prompt.md")
            if not ok_ref:
                problems.append(f"{name}: REF -> rc={r.get('rc')} pass={r.get('pass')} "
                                f"score={r.get('score')} verdict={r.get('verdict')} "
                                f"{r.get('stderr_tail','')[:80]}")
            if not ok_empty:
                problems.append(f"{name}: EMPTY -> rc={e.get('rc')} verdict={e.get('verdict')} "
                                f"crashed={e.get('grader_crashed')} {e.get('stderr_tail','')[:80]}")
            if pw > 2000:
                problems.append(f"{name}: prompt.md is {pw} words, over the 2000-word guidance")
            print(f"{name:<16} words={pw:<5} seed={len(seed_files):<3} "
                  f"REF={'ok' if ok_ref else 'BAD':<4} EMPTY={'ok' if ok_empty else 'BAD':<4} "
                  f"score={r.get('score')} verdict={r.get('verdict')}/{e.get('verdict')}",
                  flush=True)

    print("\n=== summary ===")
    print(f"candidates: {len(rows)}")
    print(f"REF ok:     {sum(1 for r in rows if r['ok_ref'])}/{len(rows)}")
    print(f"EMPTY ok:   {sum(1 for r in rows if r['ok_empty'])}/{len(rows)}")
    if problems:
        print(f"\n{len(problems)} problems:")
        for p in problems:
            print("  -", p)
    else:
        print("\nno problems found")
    with open(os.path.join(HERE, "verify-candidates.json"), "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "problems": problems}, fh, indent=1)


if __name__ == "__main__":
    main()
