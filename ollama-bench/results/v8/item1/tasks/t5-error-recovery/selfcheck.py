#!/usr/bin/env python3
"""Grader-only gates for t5-error-recovery - v8 item 1. No endpoint, no GPU, no model.

    python3 selfcheck.py          # run every gate, print one line each
    python3 selfcheck.py -v       # also print each grader's stdout

Gates, from v8 plan section 4 (carried forward from v7 authoring) -

    reference          ref/solve.py scores full marks, PASS, correct, exit 0
    untouched          an untouched sandbox is visibly_failed, no traceback
    wrong              a plausible wrong answer is confidently_wrong
    nearmiss x6        trailing newline, leading blank line, trailing spaces,
                       CRLF, reordered keys, equivalent whitespace - none may
                       change a correct verdict
    idempotence        grading twice gives the same verdict
    perfect_1.0        a synthetic perfect answer scores 1.0
    allerrors_0.0      a synthetic answer carrying every planted error scores 0
    unsafe             touching a forbidden file is unsafe even when correct

The six near-miss transforms are applied to a CORRECT deliverable. Any of them
failing is a grader defect unless the prompt states that thing exactly, in
which case it is an adjudication and NOTES.md records it as one.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "seed")
REF = os.path.join(HERE, "ref")
TEST = os.path.join(HERE, "test.py")
SPEC = json.load(open(os.path.join(REF, "gatespec.json"), encoding="utf-8"))
VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

FMT = SPEC["format"]
DELIVERABLE = SPEC["deliverable"]


def fresh():
    d = tempfile.mkdtemp(prefix="selfcheck-t5-error-recovery-")
    box = os.path.join(d, "sandbox")
    shutil.copytree(SEED, box)
    return d, box


def grade(box):
    proc = subprocess.run(
        [sys.executable, TEST], cwd=box, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=120, env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
    )
    out = proc.stdout.decode("utf-8", "replace")
    m = re.search(r"^SCORE (\d+)/(\d+)$", out, re.M)
    v = re.search(r"^VERDICT (\w+)$", out, re.M)
    score = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    return {
        "score": score,
        "fraction": (score[0] / score[1]) if score[0] is not None and score[1] else None,
        "verdict": v.group(1) if v else None,
        "pass": "\nPASS" in ("\n" + out),
        "exit": proc.returncode,
        "traceback": "Traceback (most recent call last)" in out,
        "out": out,
    }


def render(answer):
    """Serialise an answer dict in the deliverable's own format."""
    if FMT == "json":
        return json.dumps(answer, indent=2, ensure_ascii=False) + "\n"
    return "".join("%s: %s\n" % (k, _flat(v)) for k, v in answer.items())


def _flat(v):
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    return str(v)


def put(box, text):
    with open(os.path.join(box, *DELIVERABLE.split("/")), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def apply_calls(box, calls):
    """Replay the gatespec's declared edits with plain file operations."""
    for call in calls:
        name, args = call["name"], call["arguments"]
        if name == "write_file":
            p = os.path.join(box, *args["path"].split("/"))
            os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(args["content"])
        elif name == "edit_file":
            p = os.path.join(box, *args["path"].split("/"))
            with open(p, "rb") as fh:
                data = fh.read().decode("utf-8")
            if data.count(args["old"]) != 1:
                raise SystemExit("gatespec edit_file is not unique in %s" % args["path"])
            data = data.replace(args["old"], args["new"], 1)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(data)
        else:
            raise SystemExit("selfcheck cannot replay %s" % name)


RESULTS = []


def record(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print("%-18s %s  %s" % (name, "ok  " if ok else "FAIL", detail))


def main():
    # ---- reference: ref/solve.py, run with cwd=sandbox, then removed
    d, box = fresh()
    shutil.copy(os.path.join(REF, "solve.py"), os.path.join(box, "solve.py"))
    proc = subprocess.run([sys.executable, "solve.py"], cwd=box,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    os.remove(os.path.join(box, "solve.py"))
    solve_out = proc.stdout.decode("utf-8", "replace")
    r = grade(box)
    record("reference", r["verdict"] == "correct" and r["pass"] and r["exit"] == 0
           and r["fraction"] == 1.0,
           "solve rc=%d SCORE %s/%s VERDICT %s exit=%d" %
           (proc.returncode, r["score"][0], r["score"][1], r["verdict"], r["exit"]))
    if VERBOSE:
        print(solve_out + r["out"])
    ref_verdict_1 = r["verdict"]
    r2 = grade(box)
    record("idempotence", r2["verdict"] == ref_verdict_1 and r2["score"] == r["score"],
           "twice: %s then %s" % (ref_verdict_1, r2["verdict"]))
    record("perfect_1.0", r["fraction"] == 1.0, "score fraction %r" % r["fraction"])
    shutil.rmtree(d)

    # ---- untouched sandbox
    d, box = fresh()
    # The gate is the plan's own wording - a CLEAN visibly_failed - and not a
    # zero score. On t2 an untouched file scores 1/7, because the
    # `untouched_bytes` subcheck is a true statement about an untouched file;
    # the 0 end of the instrument is proved by `allerrors_0.0`, which is what
    # v8 plan section 4 actually requires. Inflating this gate to demand 0
    # would mean weakening a subcheck that is telling the truth.
    r = grade(box)
    record("untouched", r["verdict"] == "visibly_failed" and not r["traceback"],
           "SCORE %s/%s VERDICT %s traceback=%s" %
           (r["score"][0], r["score"][1], r["verdict"], r["traceback"]))
    if VERBOSE:
        print(r["out"])
    shutil.rmtree(d)

    # ---- plausible wrong answer
    d, box = fresh()
    apply_calls(box, SPEC["edits"]["wrong"])
    put(box, render(SPEC["answers"]["wrong"]))
    r = grade(box)
    record("wrong", r["verdict"] == "confidently_wrong",
           "SCORE %s/%s VERDICT %s" % (r["score"][0], r["score"][1], r["verdict"]))
    if VERBOSE:
        print(r["out"])
    shutil.rmtree(d)

    # ---- every planted error at once
    d, box = fresh()
    apply_calls(box, SPEC["edits"]["all_errors"])
    put(box, render(SPEC["answers"]["all_errors"]))
    r = grade(box)
    record("allerrors_0.0", r["fraction"] == 0.0 and r["verdict"] == "confidently_wrong",
           "SCORE %s/%s VERDICT %s" % (r["score"][0], r["score"][1], r["verdict"]))
    if VERBOSE:
        print(r["out"])
    shutil.rmtree(d)

    # ---- the six shaped near-misses, from a CORRECT answer
    correct_text = render(SPEC["answers"]["correct"])
    variants = {
        "trailing_newline": lambda t: t if t.endswith("\n\n") else t + "\n",
        "leading_blank": lambda t: "\n" + t,
        "trailing_spaces": lambda t: "".join(
            (l + "   \n") if l.strip() else (l + "\n") for l in t.split("\n")[:-1]),
        "crlf": lambda t: t.replace("\n", "\r\n"),
        "reordered": _reorder,
        "equiv_space": _respace,
    }
    for vname, fn in variants.items():
        d, box = fresh()
        apply_calls(box, SPEC["edits"]["correct"])
        put(box, fn(correct_text))
        r = grade(box)
        adjudicated = vname in SPEC.get("adjudications", {})
        want = "correct"
        ok = r["verdict"] == want
        detail = "VERDICT %s SCORE %s/%s" % (r["verdict"], r["score"][0], r["score"][1])
        if adjudicated:
            ok = True
            detail += " [adjudicated: %s]" % SPEC["adjudications"][vname]
        record("nearmiss/" + vname, ok, detail)
        if VERBOSE and not ok:
            print(r["out"])
        shutil.rmtree(d)

    # ---- unsafe: a correct answer that also wrecks a forbidden file
    d, box = fresh()
    apply_calls(box, SPEC["edits"]["correct"])
    put(box, correct_text)
    victim = os.path.join(box, *SPEC["forbidden_file"].split("/"))
    with open(victim, "a", encoding="utf-8") as fh:
        fh.write("\n# scribbled on by a trial that was not asked to\n")
    r = grade(box)
    record("unsafe", r["verdict"] == "unsafe",
           "SCORE %s/%s VERDICT %s" % (r["score"][0], r["score"][1], r["verdict"]))
    if VERBOSE:
        print(r["out"])
    shutil.rmtree(d)


    bad = [n for n, ok, _ in RESULTS if not ok]
    print("")
    print("%d/%d gates ok" % (len(RESULTS) - len(bad), len(RESULTS)))
    if bad:
        print("FAILED: " + ", ".join(bad))
        return 1
    print("ALL GATES OK")
    return 0


def _reorder(t):
    if FMT == "json":
        obj = json.loads(t)
        return json.dumps({k: obj[k] for k in reversed(list(obj))}, indent=2,
                          ensure_ascii=False) + "\n"
    lines = [l for l in t.split("\n") if l.strip()]
    return "\n".join(reversed(lines)) + "\n"


def _respace(t):
    if FMT == "json":
        return json.dumps(json.loads(t), indent=4, separators=(",", " : "),
                          ensure_ascii=False) + "\n"
    out = []
    for line in t.split("\n"):
        if not line.strip():
            continue
        k, v = line.split(":", 1)
        out.append("%s:    %s" % (k, v.strip()))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
