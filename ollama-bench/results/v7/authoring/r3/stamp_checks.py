#!/usr/bin/env python3
"""Run every CPU-only check over the round-3 candidates once, and stamp the results.

    python3 r3/stamp_checks.py            # run everything, print the block
    python3 r3/stamp_checks.py --stamp    # and write it into results/v7/authoring-r3-2026-09-08.md

This is the round's single validation run. It is slow — `validate_all.py` builds a sandbox and
grades it eight times per candidate — so it is launched detached and its marker polled, never
run in the foreground:

    setsid -f bash -c 'cd /mnt/d/local-llm-bench/ollama-bench/results/v7/authoring && \\
      python3 r3/stamp_checks.py --stamp > r3/checks.log 2>&1; touch r3/.checks-done' \\
      < /dev/null > /dev/null 2>&1

Nothing here runs a model, loads a model, or touches the GPU. It reads files, hashes files,
parses graders and grades reference answers.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
V7 = os.path.dirname(AUTHORING)
BENCH = os.path.dirname(os.path.dirname(V7))
PAGE = os.path.join(V7, "authoring-r3-2026-09-08.md")
BEGIN = "<!-- BEGIN GENERATED r3 CHECKS -->"
END = "<!-- END GENERATED r3 CHECKS -->"

PY_WIN = "/mnt/c/Users/slb/scoop/apps/python/current/python.exe"


def slots():
    out = []
    for fam in sorted(d for d in os.listdir(AUTHORING) if d.startswith("cand-")):
        base = os.path.join(AUTHORING, fam)
        for slot in sorted(os.listdir(base)):
            mp = os.path.join(base, slot, "MANIFEST.json")
            if not os.path.exists(mp):
                continue
            with open(mp, encoding="utf-8") as fh:
                if (json.load(fh) or {}).get("round") == "v7r3-difficulty":
                    out.append(os.path.join(base, slot))
    return sorted(out)


def editable_of(cand):
    """The `editable` map out of a generated grader, parsed and never imported."""
    import ast
    try:
        tree = ast.parse(open(os.path.join(cand, "test.py"), encoding="utf-8").read())
    except (OSError, SyntaxError):
        return {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CONFIG":
                    try:
                        return ast.literal_eval(node.value).get("editable") or {}
                    except ValueError:
                        return {}
    return {}


def run(cmd, cwd=BENCH, env=None, timeout=5400):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, **(env or {})), encoding="utf-8", errors="replace")
    return {"cmd": " ".join(cmd), "rc": p.returncode, "out": p.stdout, "err": p.stderr,
            "s": round(time.time() - t0, 1)}


def last(text, pred=None, n=1):
    lines = [l for l in (text or "").splitlines() if l.strip()]
    if pred:
        lines = [l for l in lines if pred(l)]
    return " / ".join(lines[-n:]) if lines else "(no output)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", action="store_true")
    a = ap.parse_args()

    cands = slots()
    rel = [os.path.relpath(c, AUTHORING) for c in cands]
    rows = []

    def add(name, r, summary):
        rows.append((name, "ok" if r["rc"] == 0 else "**FAILED (rc=%d)**" % r["rc"],
                     summary, r["s"]))

    r = run([sys.executable, "r3/check_load_bearing.py"], cwd=AUTHORING)
    add("`r3/check_load_bearing.py`", r, last(r["out"]))

    r = run([sys.executable, "r3/check_rung0.py"], cwd=AUTHORING)
    add("`r3/check_rung0.py`", r, last(r["out"]))

    r = run([sys.executable, "measure_material.py"] + rel, cwd=AUTHORING)
    add("`measure_material.py`", r, last(r["out"]))

    r = run([sys.executable, "stamp_manifests.py", "--check"] + rel, cwd=AUTHORING)
    add("`stamp_manifests.py --check`", r, last(r["out"]))

    for c in cands:
        r = run([sys.executable, "selfcheck.py"], cwd=c)
        add("`%s/selfcheck.py`" % os.path.basename(c), r,
            "%d case(s), %s" % (len([l for l in r["out"].splitlines() if " PASS " in l
                                     or " FAIL " in l]), last(r["out"])))

    r = run([sys.executable, "probe_idempotence.py"] + rel, cwd=AUTHORING)
    add("`probe_idempotence.py`", r, last(r["out"]))

    for c in cands:
        r = run([sys.executable, "probe_candidate.py", os.path.relpath(c, AUTHORING)],
                cwd=AUTHORING)
        summary = last(r["out"], lambda l: l.startswith("CLEAN") or l.startswith("  - "), n=4)
        # A task whose deliverable IS the bytes of an edited file legitimately rejects a CRLF
        # or trailing-space perturbation of that file, and probe_candidate.py cannot tell that
        # from a defect — it perturbs every file the reference changes. So the exception is
        # named here rather than assumed: it applies only when the candidate declares
        # `editable` files, only to perturbation rows, and the candidate's own selfcheck still
        # has to show the five perturbations of the DELIVERABLE landing `correct`.
        problems = [l.strip()[2:] for l in r["out"].splitlines() if l.startswith("  - ")]
        if r["rc"] != 0 and editable_of(c) and problems and all(
                pr.startswith("GRADER DEFECT: perturb:") for pr in problems):
            rows.append(("`probe_candidate.py %s`" % os.path.basename(c),
                         "ok (adjudicated)",
                         "reference passes, empty sandbox is a clean visibly_failed; %d "
                         "perturbation row(s) of the byte-exact edited file(s) fail as the "
                         "prompt states they must — NOTES.md adjudicates them" % len(problems),
                         r["s"]))
        else:
            add("`probe_candidate.py %s`" % os.path.basename(c), r, summary)

    r = run([sys.executable, "r3/stage_gate_suite.py"], cwd=AUTHORING)
    add("`r3/stage_gate_suite.py`", r, last(r["out"]))

    if os.path.exists(PY_WIN):
        env = {"V7_PROBE_BASE": r"D:\local-llm-bench\ollama-bench\results\v7\authoring\r3\gate-suite",
               "WSLENV": "V7_PROBE_BASE" + (":" + os.environ["WSLENV"]
                                            if os.environ.get("WSLENV") else "")}
        rr = run([PY_WIN, "results/v7/probe_scope_gate.py"] + [os.path.basename(c) for c in cands],
                 env=env)
        ok = sum(1 for l in rr["out"].splitlines() if "VERDICT correct" in l)
        add("`probe_scope_gate_r3.sh` (Windows interpreter)", rr,
            "%d of %d references `correct` under %s"
            % (ok, len(cands), rr["out"].splitlines()[0].split()[1]
               if rr["out"].strip() else "?"))
        rb = run([PY_WIN, "results/v7/probe_scope_gate.py", "--breach"]
                 + [os.path.basename(c) for c in cands], env=env)
        fired = sum(1 for l in rb["out"].splitlines() if "VERDICT unsafe" in l)
        add("`probe_scope_gate_r3.sh --breach`", rb,
            "%d of %d scope gates fired on a planted stray file" % (fired, len(cands)))
    else:
        rows.append(("`probe_scope_gate_r3.sh`", "**not run**",
                     "the Windows interpreter was not found at %s" % PY_WIN, 0))

    r = run([sys.executable, "results/v7/probe_read_paths.py"])
    add("`results/v7/probe_read_paths.py`", r, last(r["out"], lambda l: "case(s)" in l))

    r = run([sys.executable, "results/v7/probe_coverage_gate.py"])
    add("`results/v7/probe_coverage_gate.py`", r,
        last(r["out"], lambda l: "candidate(s) probed" in l))

    r = run([sys.executable, "results/v7/coverage_gate.py", "--verify-calibration"])
    add("`results/v7/coverage_gate.py --verify-calibration`", r,
        last(r["out"], lambda l: "figure(s) checked" in l))

    r = run([sys.executable, "validate_all.py"], cwd=AUTHORING)
    add("`validate_all.py` (all candidates, round 1 and round 3)", r,
        last(r["out"], lambda l: "candidate(s)" in l))

    r = run(["bash", "results/v7/run_gpu_round.sh"])
    add("`run_gpu_round.sh` (no `--go`)", r,
        "dry run: %s" % last(r["out"], lambda l: "DRY RUN" in l or "PREFLIGHT" in l))

    L = ["| check | result | what it said | s |", "| --- | --- | --- | ---: |"]
    for name, state, summary, secs in rows:
        L.append("| %s | %s | %s | %.0f |"
                 % (name, state, summary.replace("|", "\\|")[:220], secs))
    body = "\n".join(L)
    failed = [n for n, s, _u, _t in rows if not s.startswith("ok")]
    body += ("\n\n**%d check(s), %d not ok.**" % (len(rows), len(failed)))
    if failed:
        body += " Not ok: " + ", ".join(failed) + "."

    print(body)
    if a.stamp:
        text = open(PAGE, encoding="utf-8").read()
        head, rest = text.split(BEGIN, 1)
        _old, tail = rest.split(END, 1)
        with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(head + BEGIN + "\n\n" + body + "\n\n" + END + tail)
        print("\nstamped into %s" % PAGE)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
