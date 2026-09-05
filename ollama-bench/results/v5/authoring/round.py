"""Assemble, prep and grade a desaturation round of the v5 suite.

A round is a suite directory (task -> chosen candidate) plus per-trial sandboxes graded exactly
as pibench.py grades: seed/ only into the sandbox, test.py copied in as _hidden_test.py, run with
cwd=sandbox, PYTHONUTF8=1, PYTHONIOENCODING=utf-8, 60 s timeout; pass iff rc==0 and 'PASS' in
stdout; SCORE and VERDICT parsed from stdout.

  python3 round.py build <round-dir> <task>=<cand> [<task>=<cand> ...]
  python3 round.py prep  <round-dir> <arm> <trial>
  python3 round.py grade <round-dir> <arm> <trial>
  python3 round.py tally <round-dir> <arm>

Layout:
  <round-dir>/suite/<task>/{prompt.md,seed/,ref/,test.py}
  <round-dir>/<arm>/trial-<n>/<task>/            the sandbox the model works in
  <round-dir>/<arm>/trial-<n>/results.json
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "tasks-v5"))
SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)


def suite_dir(rd, trial=None):
    """A round normally has one `suite/`. A round that ROTATES a task's variants across
    trials has `suite-0/`, `suite-1/`, ... instead: trial N is graded against the variant
    that trial N was given. Rotation is what stops a one-bit task -- "is the docstring
    accurate, yes or no" -- being scored 3/3 by a model that guessed the bit once and held
    it. Arity is unchanged: the task still contributes three trials."""
    if trial is not None:
        per = os.path.join(rd, f"suite-{trial}")
        if os.path.isdir(per):
            return per
    return os.path.join(rd, "suite")


def tasks(rd, trial=None):
    s = suite_dir(rd, trial)
    return sorted(t for t in os.listdir(s) if os.path.isdir(os.path.join(s, t)))


def build(rd, pairs, trial=None):
    s = suite_dir(rd, trial) if trial is None else os.path.join(rd, f"suite-{trial}")
    if os.path.exists(s):
        shutil.rmtree(s)
    os.makedirs(s)
    mapping = {}
    for p in pairs:
        # Two forms. "<task>=<cand>" places the candidate under its own task name, which is
        # what a scored suite wants. "<label>=<task>/<cand>" places it under an arbitrary
        # label, so several candidates of the SAME task can sit in one suite -- that is how
        # a variant sweep asks "is a harder variant already on disk?" in one arm.
        label, spec = p.split("=", 1)
        task, cand = spec.split("/", 1) if "/" in spec else (label, spec)
        src = os.path.join(TASKS, task, cand)
        if not os.path.isdir(src):
            raise SystemExit(f"no such candidate: {src}")
        dst = os.path.join(s, label)
        os.makedirs(dst)
        for name in ("prompt.md", "test.py"):
            shutil.copy(os.path.join(src, name), os.path.join(dst, name))
        for name in ("seed", "ref"):
            sp = os.path.join(src, name)
            if os.path.isdir(sp):
                shutil.copytree(sp, os.path.join(dst, name),
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        mapping[label] = f"{task}/{cand}"
        print(f"{label} <- {task}/{cand}")
    name = "mapping.json" if trial is None else f"mapping-{trial}.json"
    json.dump(mapping, open(os.path.join(rd, name), "w"), indent=1)


def prep(rd, arm, trial, only=None):
    """DESTRUCTIVE: it deletes and recreates each sandbox it touches. Pass `only` to
    re-prep a single task -- re-prepping the whole arm to fix one task destroys every
    completed-but-ungraded sandbox in it, which cost this session about twenty finished
    reference-model runs on 2026-09-05."""
    for t in tasks(rd, trial):
        if only and t not in only:
            continue
        sb = os.path.join(rd, arm, f"trial-{trial}", t)
        if os.path.exists(sb):
            shutil.rmtree(sb)
        os.makedirs(sb)
        seed = os.path.join(suite_dir(rd, trial), t, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sb, dirs_exist_ok=True)
        print(f"{t}: {sb}")


def grade(rd, arm, trial, only=None):
    """Grades every task, or only the named ones. A scoped grade MERGES into the existing
    results.json rather than replacing it, so re-grading one task cannot silently turn the
    other seven into failures against emptied sandboxes."""
    out_p = os.path.join(rd, arm, f"trial-{trial}", "results.json")
    out = json.load(open(out_p)) if (only and os.path.isfile(out_p)) else {}
    for t in tasks(rd, trial):
        if only and t not in only:
            continue
        sb = os.path.join(rd, arm, f"trial-{trial}", t)
        if not os.path.isdir(sb):
            out[t] = {"error": "no sandbox", "pass": False}
            continue
        hidden = os.path.join(sb, "_hidden_test.py")
        shutil.copy(os.path.join(suite_dir(rd, trial), t, "test.py"), hidden)
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            so, rc = p.stdout, p.returncode
        except subprocess.TimeoutExpired:
            so, rc = "", -1
        os.remove(hidden)
        sc = SCORE_RE.findall(so)
        vd = VERDICT_RE.findall(so)
        out[t] = {"pass": rc == 0 and "PASS" in so,
                  "score": f"{sc[-1][0]}/{sc[-1][1]}" if sc else None,
                  "verdict": vd[-1] if vd else None, "rc": rc,
                  "tail": so.strip()[-200:]}
        r = out[t]
        print(f"{t:5s} {'PASS' if r['pass'] else 'FAIL':4s} score={r['score']} "
              f"verdict={r['verdict']}")
    json.dump(out, open(out_p, "w", encoding="utf-8"), indent=1)
    n = sum(1 for v in out.values() if v.get("pass"))
    print(f"\n{n}/{len(out)} passed -> {out_p}")


def tally(rd, arm):
    base = os.path.join(rd, arm)
    trials = sorted(d for d in os.listdir(base) if d.startswith("trial-"))
    per = {}
    for tr in trials:
        p = os.path.join(base, tr, "results.json")
        if not os.path.isfile(p):
            continue
        for task, r in json.load(open(p)).items():
            per.setdefault(task, []).append((tr, r.get("pass"), r.get("verdict")))
    tot = ok = 0
    print(f"{'task':6s}{'passes':>10s}  verdicts")
    for task in sorted(per):
        rows = per[task]
        n = sum(1 for _, p_, _ in rows if p_)
        tot += len(rows)
        ok += n
        print(f"{task:6s}{n:>7d}/{len(rows):<3d} " +
              ", ".join(f"{v}" for _, _, v in rows))
    print(f"\n{arm}: {ok}/{tot} = {100.0*ok/tot:.1f}%" if tot else f"{arm}: no trials")


if __name__ == "__main__":
    mode = sys.argv[1]
    rd = os.path.abspath(sys.argv[2])
    os.makedirs(rd, exist_ok=True)
    if mode == "build":
        # build <round> [--trial N] <pairs...>
        args = sys.argv[3:]
        tr = None
        if args and args[0] == "--trial":
            tr, args = args[1], args[2:]
        build(rd, args, tr)
    elif mode == "prep":
        prep(rd, sys.argv[3], sys.argv[4],
             set(sys.argv[5].split(",")) if len(sys.argv) > 5 else None)
    elif mode == "grade":
        grade(rd, sys.argv[3], sys.argv[4],
              set(sys.argv[5].split(",")) if len(sys.argv) > 5 else None)
    elif mode == "tally":
        tally(rd, sys.argv[3])
    else:
        raise SystemExit(__doc__)
