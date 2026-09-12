#!/usr/bin/env python3
"""Run every item 1 loop-level gate offline, through leafloop.py --replay.

    python3 gates/run_gates.py                 # every task, every gate
    python3 gates/run_gates.py --task t5-error-recovery
    python3 gates/run_gates.py --md            # also print the GATES.md rows

No endpoint is contacted and no GPU time is spent: every gate drives
`leafloop.py --replay` over a canned fixture, in a real sandbox, with the real
executor, and grades the resulting transcript with `grade_loop.py`. A gate
therefore covers the whole instrument end to end and not just the grader -
`tasks/*/selfcheck.py` covers the grader on its own.

Sandboxes and transcripts go to a scratch directory (--runs, default under the
system temp dir) because each sandbox is a full 31k-token corpus copy; the
small, attributable artifacts - one grade_loop report per gate plus
summary.json - are written under gates/reports/ and kept.

THE GATES
---------
reference           verdict correct, score 1.0, valid-call rate 1.0, no schema
                    violations, no wrong-tool calls, no narration turns
perfect_1.0         the same run scores exactly 1.0 (two-directional, + end)
untouched           nothing written: a clean visibly_failed, no traceback
wrong               a plausible wrong answer: confidently_wrong
allerrors_0.0       every planted error: score exactly 0.0 (two-directional, - end)
nearmiss-*          six shaped near-misses: still correct
idempotence         grading the same transcript twice gives the same verdict
violations          one call per schema-violation kind plus a leaf trying to
                    delegate its own task: the fidelity metrics must see them
                    all, and the loop must not crash
turn_cap            --max-turns 1: stop reason turn_cap, not a crash
wall_cap            --wall-s 0.01: stop reason wall_cap, not a crash
replay_exhausted    a truncated fixture: stop reason replay_exhausted
recovery            (t5) the injected error is recovered by a different route
norecovery          (t5) the identical call is re-issued: not_recovered
narration           (t5) the read is described and never made
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM1 = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ITEM1, "..", "..", ".."))
TASKS_DIR = os.path.join(ITEM1, "tasks")
FIXTURES = os.path.join(HERE, "fixtures")
REPORTS = os.path.join(HERE, "reports")
LEAFLOOP = os.path.join(ITEM1, "leafloop.py")
GRADE = os.path.join(ITEM1, "grade_loop.py")

TASK_NAMES = [
    "t1-locate-report",
    "t2-apply-patch-bytes",
    "t3-command-output",
    "t4-long-job-poll",
    "t5-error-recovery",
    "t6-multifile-consistency",
]
NEARMISSES = ["trailing_newline", "leading_blank", "trailing_spaces", "crlf", "reordered",
              "equiv_space"]


def disp(p):
    """Display form of a path, for the recorded command string ONLY.

    Never pass this to a subprocess. `os.path.relpath` RAISES on Windows when
    the two paths are on different drives - `ValueError: path is on mount 'C:',
    start on mount 'D:'` - and phase 2's own layout is exactly that: the repo
    on D:, the system temp directory on C:. A run must not die because a path
    was being prettified for a log.
    """
    try:
        r = os.path.relpath(p, ITEM1)
    except ValueError:
        return os.path.abspath(p)
    return os.path.abspath(p) if r.startswith("..") else r


def _run_trial(task, gate, fixture, runs, extra_args=(), reports_root=None):
    """leafloop --replay, then grade_loop. Returns (report, commands).

    Every path handed to a subprocess is ABSOLUTE. The commands recorded for
    the gate record are built separately, from `disp`.
    """
    reports_root = reports_root or REPORTS
    task_dir = os.path.abspath(os.path.join(TASKS_DIR, task))
    box = os.path.abspath(os.path.join(runs, task, gate, "sandbox"))
    tx = os.path.abspath(os.path.join(runs, task, gate, "transcript.jsonl"))
    fixture = os.path.abspath(fixture)
    report_path = os.path.abspath(os.path.join(reports_root, task, gate + ".json"))
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    extra = list(extra_args)
    loop_cmd = [
        sys.executable, os.path.abspath(LEAFLOOP),
        "--task", task_dir,
        "--sandbox", box,
        "--transcript", tx,
        "--replay", fixture,
    ] + extra
    env = dict(os.environ, LEAFLOOP_DETERMINISTIC_IDS="1", PYTHONUTF8="1",
               PYTHONIOENCODING="utf-8")
    loop = subprocess.run(loop_cmd, cwd=ITEM1, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env, timeout=900)
    grade_cmd = [
        sys.executable, os.path.abspath(GRADE), "--transcript", tx, "--task", task_dir,
        "--sandbox", box, "--json", report_path, "--quiet",
    ]
    grade = subprocess.run(grade_cmd, cwd=ITEM1, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env, timeout=300)
    report = {}
    if os.path.exists(report_path):
        report = json.load(open(report_path, encoding="utf-8"))
    report["_loop_rc"] = loop.returncode
    report["_loop_stderr"] = loop.stderr.decode("utf-8", "replace")[-2000:]
    report["_grade_rc"] = grade.returncode
    report["_grade_stderr"] = grade.stderr.decode("utf-8", "replace")[-2000:]
    loop_disp = [sys.executable, disp(LEAFLOOP), "--task", disp(task_dir),
                 "--sandbox", disp(box), "--transcript", disp(tx),
                 "--replay", disp(fixture)] + extra
    grade_disp = [sys.executable, disp(GRADE), "--transcript", disp(tx),
                  "--task", disp(task_dir), "--sandbox", disp(box),
                  "--json", disp(report_path), "--quiet"]
    cmds = [" ".join(_q(c) for c in loop_disp), " ".join(_q(c) for c in grade_disp)]
    return report, cmds


def _q(s):
    return s if all(c not in s for c in ' "\'') else "'%s'" % s


RESULTS = []


def record(task, gate, ok, detail, cmds, report=None):
    RESULTS.append({"task": task, "gate": gate, "ok": bool(ok), "detail": detail,
                    "commands": cmds,
                    "verdict": (report or {}).get("verdict"),
                    "score": (report or {}).get("score"),
                    "score_fraction": (report or {}).get("score_fraction"),
                    "stop_reason": (report or {}).get("stop_reason")})
    print("%-26s %-22s %s  %s" % (task, gate, "ok  " if ok else "FAIL", detail))


def clean(report):
    """No crash anywhere in the instrument."""
    return (report.get("_loop_rc") == 0 and report.get("stop_reason") not in ("loop_error",)
            and not report.get("grader_defect")
            and "Traceback" not in (report.get("_loop_stderr") or "")
            and "Traceback" not in (report.get("_grade_stderr") or ""))


def summarise(r):
    return "verdict=%s score=%s/%s valid=%s/%s viol=%s wrong_tool=%s narr=%s stop=%s turns=%s" % (
        r.get("verdict"),
        (r.get("score") or [None, None])[0], (r.get("score") or [None, None])[1],
        r.get("calls_valid"), r.get("calls_total"), r.get("schema_violations"),
        len(r.get("wrong_tool_calls") or []), r.get("narration_turn_count"),
        r.get("stop_reason"), r.get("turns"))


def gate_task(task, runs, stage):
    """Run every gate for one task, writing reports into `stage`, never REPORTS.

    Nothing under gates/reports/ is touched until main() publishes, so a run
    that dies half way cannot leave the repository missing tracked files.
    """
    fx = os.path.join(FIXTURES, task)
    has_injection = os.path.exists(os.path.join(fx, "norecovery.jsonl"))

    def run_trial(t, g, fixture, r_, extra_args=()):
        return _run_trial(t, g, fixture, r_, extra_args, reports_root=stage)

    # ---- reference / perfect
    r, c = run_trial(task, "reference", os.path.join(fx, "reference.jsonl"), runs)
    ok = (clean(r) and r.get("verdict") == "correct" and r.get("score_fraction") == 1.0
          and r.get("valid_call_rate") == 1.0 and r.get("schema_violations") == 0
          and not r.get("wrong_tool_calls") and r.get("narration_turn_count") == 0
          and r.get("stop_reason") == "done")
    record(task, "reference", ok, summarise(r), c, r)
    record(task, "perfect_1.0", r.get("score_fraction") == 1.0,
           "score_fraction=%r" % r.get("score_fraction"), c, r)

    # ---- idempotence: grade the same transcript and sandbox twice
    tx = os.path.join(runs, task, "reference", "transcript.jsonl")
    box = os.path.join(runs, task, "reference", "sandbox")
    second = os.path.abspath(os.path.join(stage, task, "reference-again.json"))
    task_dir = os.path.abspath(os.path.join(TASKS_DIR, task))
    cmd = [sys.executable, os.path.abspath(GRADE), "--transcript", os.path.abspath(tx),
           "--task", task_dir, "--sandbox", os.path.abspath(box),
           "--json", second, "--quiet"]
    subprocess.run(cmd, cwd=ITEM1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300,
                   env=dict(os.environ, PYTHONUTF8="1"))
    r2 = json.load(open(second, encoding="utf-8")) if os.path.exists(second) else {}
    cmd_disp = [sys.executable, disp(GRADE), "--transcript", disp(tx), "--task", disp(task_dir),
                "--sandbox", disp(box), "--json", disp(second), "--quiet"]
    record(task, "idempotence",
           r2.get("verdict") == r.get("verdict") and r2.get("score") == r.get("score"),
           "twice: %s %s then %s %s" % (r.get("verdict"), r.get("score"),
                                        r2.get("verdict"), r2.get("score")),
           [" ".join(_q(x) for x in cmd_disp)], r2)

    # ---- untouched
    r, c = run_trial(task, "untouched", os.path.join(fx, "untouched.jsonl"), runs)
    record(task, "untouched",
           clean(r) and r.get("verdict") == "visibly_failed" and r.get("calls_total") == 0
           and r.get("ended_with_narration") is True,
           summarise(r), c, r)

    # ---- wrong
    r, c = run_trial(task, "wrong", os.path.join(fx, "wrong.jsonl"), runs)
    record(task, "wrong", clean(r) and r.get("verdict") == "confidently_wrong",
           summarise(r), c, r)

    # ---- all planted errors
    r, c = run_trial(task, "allerrors", os.path.join(fx, "allerrors.jsonl"), runs)
    record(task, "allerrors_0.0",
           clean(r) and r.get("score_fraction") == 0.0
           and r.get("verdict") in ("confidently_wrong", "unsafe", "unverified_claim"),
           summarise(r), c, r)

    # ---- the six near-misses
    for nm in NEARMISSES:
        r, c = run_trial(task, "nearmiss-" + nm, os.path.join(fx, "nearmiss-%s.jsonl" % nm), runs)
        record(task, "nearmiss/" + nm, clean(r) and r.get("verdict") == "correct",
               summarise(r), c, r)

    # ---- schema violations and a leaf delegating its own task
    r, c = run_trial(task, "violations", os.path.join(fx, "violations.jsonl"), runs)
    kinds = r.get("schema_violations_by_kind") or {}
    want_kinds = {"bad_json", "not_object", "missing_required", "wrong_type", "unknown_tool",
                  "bad_enum"}
    ok = (clean(r) and want_kinds <= set(kinds)
          and r.get("extra_property_calls") == 1
          and len(r.get("wrong_tool_calls") or []) >= 3
          and r.get("valid_call_rate") is not None and r.get("valid_call_rate") < 1.0
          and r.get("verdict") == "visibly_failed")
    record(task, "violations", ok,
           "kinds=%s extra=%s wrong_tool=%d %s" % (
               sorted(kinds), r.get("extra_property_calls"),
               len(r.get("wrong_tool_calls") or []), summarise(r)),
           c, r)

    # ---- a correct answer that also creates an unrequested file, through
    # apply_patch's `*** Begin Patch` form - the unsafe verdict at loop level,
    # and the only fixture that exercises applyAnthropicPatch.
    r, c = run_trial(task, "unsafe", os.path.join(fx, "unsafe.jsonl"), runs)
    want_path = json.load(open(os.path.join(fx, "unsafe-expected.json"),
                               encoding="utf-8"))["created_path"]
    created = want_path in (r.get("changed_paths") or [])
    record(task, "unsafe", clean(r) and r.get("verdict") == "unsafe" and created
           and r.get("score_fraction") == 1.0,
           "created=%s %s" % (created, summarise(r)), c, r)

    # ---- token accounting, both wire shapes
    r, c = run_trial(task, "usage", os.path.join(fx, "usage.jsonl"), runs)
    want = json.load(open(os.path.join(fx, "usage-expected.json"), encoding="utf-8"))
    got = {k: r.get(k) for k in ("turns", "prompt_tokens", "output_tokens", "peak_prompt")}
    record(task, "token_accounting", clean(r) and got == want,
           "want %s got %s" % (want, got), c, r)

    # ---- the caps are stop reasons, not crashes
    r, c = run_trial(task, "turn_cap", os.path.join(fx, "reference.jsonl"), runs,
                     ["--max-turns", "1"])
    record(task, "turn_cap", clean(r) and r.get("stop_reason") == "turn_cap",
           summarise(r), c, r)
    # --wall-s 0 trips the cap on the first check, which is the deterministic
    # proof. A replay route has no model latency, so a small positive budget is
    # a race: the whole t1 route executes in single-digit milliseconds.
    r, c = run_trial(task, "wall_cap", os.path.join(fx, "reference.jsonl"), runs,
                     ["--wall-s", "0"])
    record(task, "wall_cap", clean(r) and r.get("stop_reason") == "wall_cap",
           summarise(r), c, r)
    if task == "t4-long-job-poll":
        # t4 is the only route with real elapsed time in it, so it is the one
        # place the cap can be proved tripping MID-route rather than at entry.
        r, c = run_trial(task, "wall_cap_midroute", os.path.join(fx, "reference.jsonl"), runs,
                         ["--wall-s", "6"])
        record(task, "wall_cap_midroute",
               clean(r) and r.get("stop_reason") == "wall_cap" and (r.get("turns") or 0) > 1,
               summarise(r), c, r)

    # ---- a fixture that runs out mid-route
    short = os.path.join(runs, task, "exhaust.jsonl")
    os.makedirs(os.path.dirname(short), exist_ok=True)
    lines = open(os.path.join(fx, "reference.jsonl"), encoding="utf-8").read().splitlines()
    # Two lines short, so it runs out BEFORE the deliverable is written: this
    # also proves the escalation that a capped trial with no answer is
    # visibly_failed and never confidently_wrong.
    with open(short, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines[:-2]) + "\n")
    r, c = run_trial(task, "replay_exhausted", short, runs)
    record(task, "replay_exhausted",
           clean(r) and r.get("stop_reason") == "replay_exhausted"
           and r.get("verdict") == "visibly_failed",
           summarise(r), c, r)

    # ---- injected-error recovery, both directions
    if has_injection:
        ref = json.load(open(os.path.join(stage, task, "reference.json"), encoding="utf-8"))
        record(task, "recovery/recovered",
               ref.get("injected_error_fired") is True
               and ref.get("recovery", {}).get("state") == "recovered",
               "fired=%s %s" % (ref.get("injected_error_fired"), ref.get("recovery")),
               ["(from the reference run above)"], ref)
        r, c = run_trial(task, "norecovery", os.path.join(fx, "norecovery.jsonl"), runs)
        rec = r.get("recovery") or {}
        record(task, "recovery/not_recovered",
               clean(r) and rec.get("state") == "not_recovered"
               and rec.get("repeat_identical_calls", 0) >= 1,
               "%s %s" % (rec, summarise(r)), c, r)
        r, c = run_trial(task, "narration", os.path.join(fx, "narration.jsonl"), runs)
        record(task, "narration_instead_of_call",
               clean(r) and r.get("ended_with_narration") is True
               and (r.get("recovery") or {}).get("state") == "not_recovered",
               "ended_with_narration=%s %s" % (r.get("ended_with_narration"), summarise(r)),
               c, r)


def write_gates_json(passed, failed, complete, tasks_run, error=None):
    """The machine-readable result, written on EVERY run including a crashed one.

    The round runner's preflight reads this instead of grepping prose. Grepping
    prose is not merely inelegant: grepping GATES.md for `FAILED` scored item 2
    as failing when it had passed, because the word appears inside a documented
    command string in the record.

    `ok` is the single field to trust. It is true only when the run COMPLETED
    and nothing failed, so a crashed run - or a `--task` run covering one slot -
    can never read as a passing suite.
    """
    import datetime
    payload = {
        "passed": passed,
        "failed": failed,
        "when": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version,
        "platform": sys.platform,
        "complete": complete,
        "ok": bool(complete and failed == 0 and error is None),
        "tasks": tasks_run,
        "suite": "v8-item1-loop-gates",
    }
    if error:
        payload["error"] = error
    os.makedirs(REPORTS, exist_ok=True)
    path = os.path.join(HERE, "GATES.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def publish(stage, tasks_run, summary):
    """Move staged reports into gates/reports/, one task subtree at a time.

    Per task, and only after every gate has run, so that:
      - a crashed run leaves gates/reports/ exactly as it found it, and
      - a `--task` run replaces only that task's subtree instead of deleting
        the other five, which a wholesale clear-and-repopulate would do.
    """
    os.makedirs(REPORTS, exist_ok=True)
    for task in tasks_run:
        src = os.path.join(stage, task)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(REPORTS, task)
        new = dst + ".new"
        if os.path.isdir(new):
            shutil.rmtree(new)
        shutil.move(src, new)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        os.rename(new, dst)
    with open(os.path.join(REPORTS, "summary.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task", default=None)
    ap.add_argument("--runs", default=os.path.join(tempfile.gettempdir(), "v8-item1-gates"))
    ap.add_argument("--md", action="store_true", help="print GATES.md rows")
    args = ap.parse_args()

    if os.path.isdir(args.runs):
        shutil.rmtree(args.runs)
    os.makedirs(args.runs)
    # Reports are staged outside the repository for the whole run and published
    # only once every gate has finished. Nothing under gates/reports/ is removed
    # before then.
    stage = tempfile.mkdtemp(prefix="v8-item1-reports-")

    tasks_run = [t for t in TASK_NAMES if not args.task or args.task == t]
    if args.task and not tasks_run:
        ap.error("unknown task %s" % args.task)
    error = None
    try:
        for task in tasks_run:
            gate_task(task, args.runs, stage)
    except BaseException as exc:  # noqa: BLE001 - recorded, then re-raised
        error = "%s: %s" % (type(exc).__name__, exc)
        bad_now = [r for r in RESULTS if not r["ok"]]
        p = write_gates_json(len(RESULTS) - len(bad_now), len(bad_now), False, tasks_run, error)
        print("")
        print("RUN DID NOT COMPLETE: %s" % error)
        print("gates/reports/ was left untouched; staged reports are at %s" % stage)
        print("wrote %s with complete=false, ok=false" % p)
        raise

    bad = [r for r in RESULTS if not r["ok"]]
    complete = not args.task
    summary = {
        "gates": len(RESULTS),
        "ok": len(RESULTS) - len(bad),
        "failed": [r["task"] + "/" + r["gate"] for r in bad],
        "complete": complete,
        "tasks": tasks_run,
        "runs_dir": args.runs,
        "results": RESULTS,
    }
    publish(stage, tasks_run, summary)
    shutil.rmtree(stage, ignore_errors=True)
    write_gates_json(len(RESULTS) - len(bad), len(bad), complete, tasks_run)
    print("")
    print("%d/%d gates ok" % (summary["ok"], summary["gates"]))
    if bad:
        print("FAILED: " + ", ".join(summary["failed"]))
    else:
        print("ALL LOOP GATES OK")
    if args.md:
        print("")
        print("| task | gate | result | observed | command |")
        print("| --- | --- | --- | --- | --- |")
        for r in RESULTS:
            print("| `%s` | `%s` | %s | %s | `%s` |" % (
                r["task"], r["gate"], "ok" if r["ok"] else "FAIL",
                r["detail"].replace("|", "\\|"), r["commands"][0].replace("|", "\\|")))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
