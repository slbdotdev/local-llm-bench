"""Probe every checker in a suite with a deliberately shaped near-miss set.

Why this exists: one v5 checker scored a completely CORRECT answer as `visibly_failed`
because it required the deliverable to end in exactly one newline. One reference model
always emits that newline and another does not, so the primary metric carried a
model-dependent bias for a whole gate round. `verify_candidates.py` could not catch it --
the reference solution is written by the same hand and habits as the checker.

Method. Build the reference sandbox (seed/ + ref/, running solve.py if that is the
convention). Identify the deliverables: every text file in that sandbox that is absent
from seed/ or differs from it. Then, one perturbation at a time, rewrite a deliverable in
a way the prompt does not forbid and re-run the checker. Any of these that turns a PASS
into a FAIL is a checker defect, not a hard task:

  no_trailing_newline   correct content, final newline stripped
  extra_trailing_nl     correct content, one extra blank line at the end
  crlf                  correct content, CRLF line endings
  leading_blank         correct content, one leading blank line
  trailing_spaces       correct content, two spaces appended to each non-empty line

Usage:
  python3 probe_checkers.py <suite-dir> [--json out.json]

<suite-dir> holds <task>/{prompt.md,seed/,ref/,test.py}, i.e. round.py's `suite`
directory or authoring/gate-suite.
"""
import json, os, re, shutil, subprocess, sys, tempfile

SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)
BINARY_EXT = (".pyc", ".pyo", ".png", ".jpg", ".zip", ".gz")

PERTURBATIONS = {
    "no_trailing_newline": lambda s: s.rstrip("\n"),
    "extra_trailing_nl": lambda s: s + "\n",
    "crlf": lambda s: s.replace("\r\n", "\n").replace("\n", "\r\n"),
    "leading_blank": lambda s: "\n" + s,
    "trailing_spaces": lambda s: "".join(
        (ln + "  \n" if ln.strip() else ln + "\n") for ln in s.split("\n")[:-1]
    ) + s.split("\n")[-1] if s.endswith("\n") else s,
}


def build_ref(task_dir, dest):
    seed = os.path.join(task_dir, "seed")
    if os.path.isdir(seed):
        shutil.copytree(seed, dest, dirs_exist_ok=True)
    ref = os.path.join(task_dir, "ref")
    if os.path.isdir(ref):
        shutil.copytree(ref, dest, dirs_exist_ok=True)
    solve = os.path.join(dest, "solve.py")
    if os.path.isfile(solve):
        subprocess.run([sys.executable, "solve.py"], cwd=dest,
                       env=dict(os.environ, PYTHONUTF8="1"),
                       capture_output=True, timeout=60)
        os.remove(solve)


def run_checker(task_dir, sandbox):
    hidden = os.path.join(sandbox, "_hidden_test.py")
    shutil.copy(os.path.join(task_dir, "test.py"), hidden)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60)
        out, rc = p.stdout, p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "", -1
    finally:
        if os.path.isfile(hidden):
            os.remove(hidden)
    sc = SCORE_RE.findall(out)
    vd = VERDICT_RE.findall(out)
    return {"pass": rc == 0 and "PASS" in out, "rc": rc,
            "score": f"{sc[-1][0]}/{sc[-1][1]}" if sc else None,
            "verdict": vd[-1] if vd else None}


def deliverables(task_dir, sandbox):
    """Text files the reference produced or changed relative to seed/."""
    seed = os.path.join(task_dir, "seed")
    out = []
    for root, dirs, files in os.walk(sandbox):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for f in files:
            if f.endswith(BINARY_EXT) or f == "_hidden_test.py":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, sandbox)
            sp = os.path.join(seed, rel)
            try:
                cur = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if os.path.isfile(sp):
                try:
                    if open(sp, encoding="utf-8").read() == cur:
                        continue
                except (UnicodeDecodeError, OSError):
                    continue
            out.append(rel)
    return sorted(out)


def probe(suite):
    rows, defects = [], []
    for task in sorted(t for t in os.listdir(suite) if os.path.isdir(os.path.join(suite, t))):
        td = os.path.join(suite, task)
        base = tempfile.mkdtemp(prefix="probe_")
        try:
            build_ref(td, base)
            ref_res = run_checker(td, base)
            dels = deliverables(td, base)
            row = {"task": task, "ref": ref_res, "deliverables": dels, "probes": {}}
            if not ref_res["pass"]:
                defects.append(f"{task}: reference does not pass ({ref_res})")
                rows.append(row)
                continue
            for name, fn in PERTURBATIONS.items():
                results = {}
                for rel in dels:
                    sb = tempfile.mkdtemp(prefix="probe_")
                    try:
                        shutil.copytree(base, sb, dirs_exist_ok=True)
                        p = os.path.join(sb, rel)
                        orig = open(p, encoding="utf-8", newline="").read()
                        new = fn(orig)
                        if new == orig:
                            results[rel] = "no-op"
                            continue
                        open(p, "w", encoding="utf-8", newline="").write(new)
                        r = run_checker(td, sb)
                        results[rel] = "pass" if r["pass"] else f"FAIL({r['score']},{r['verdict']})"
                        if not r["pass"]:
                            defects.append(f"{task}: {name} on {rel} -> {results[rel]}")
                    finally:
                        shutil.rmtree(sb, ignore_errors=True)
                row["probes"][name] = results
            rows.append(row)
            worst = [f"{n}:{rel}" for n, d in row["probes"].items()
                     for rel, v in d.items() if v.startswith("FAIL")]
            print(f"{task:5s} ref=pass deliverables={len(dels)} "
                  f"{'clean' if not worst else 'DEFECTS ' + ','.join(worst)}", flush=True)
        finally:
            shutil.rmtree(base, ignore_errors=True)
    return rows, defects


if __name__ == "__main__":
    suite = os.path.abspath(sys.argv[1])
    rows, defects = probe(suite)
    print("\n=== summary ===")
    print(f"tasks probed: {len(rows)}")
    if defects:
        print(f"{len(defects)} defects:")
        for d in defects:
            print("  -", d)
    else:
        print("no format-strictness defects found")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump({"rows": rows, "defects": defects}, open(out, "w"), indent=1)
        print("wrote", out)
