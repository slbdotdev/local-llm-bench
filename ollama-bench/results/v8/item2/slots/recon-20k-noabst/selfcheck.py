"""Gate probes for recon-20k-noabst, run against its own grader. Generated; edit the generator.
Exits 0 only when every case lands on the verdict the spec declares.
"""
CASES = [{'answer': {'conflict_count': 14,
             'gov_a': {'rule': 'ratified_record_governs', 'source': 'CR-1031', 'value': 621},
             'gov_b': 'INSUFFICIENT',
             'gov_c': {'rule': 'superseded_by_later_record', 'source': 'CR-1003', 'value': 134},
             'gov_d': 'INSUFFICIENT',
             'gov_e': 'INSUFFICIENT',
             'gov_f': {'rule': 'record_does_not_govern', 'source': 'SPEC-5.7', 'value': 822},
             'gov_g': {'rule': 'specification_governs', 'source': 'SPEC-4.1', 'value': 489},
             'reconciled_total': 5960,
             'review_interval': 'INSUFFICIENT',
             'superseded_records': ['CR-1005', 'CR-1018', 'CR-1047'],
             'top_five': ['retry_backlog_count',
                          'spill_stride_mb',
                          'probe_capacity_kb',
                          'compact_horizon_mb',
                          'quota_attempts_rows']},
  'name': 'reference',
  'score': '16/16',
  'verdict': 'correct'},
 {'answer': None,
  'name': 'untouched sandbox (no answer.json)',
  'no_traceback': True,
  'verdict': 'visibly_failed'},
 {'name': 'empty file', 'no_traceback': True, 'raw': '', 'verdict': 'visibly_failed'},
 {'answer': {}, 'name': 'empty JSON object', 'no_traceback': True, 'verdict': 'visibly_failed'},
 {'answer': {'conflict_count': 14,
             'gov_a': {'rule': 'ratified_record_governs', 'source': 'CR-1031', 'value': 621},
             'gov_b': {'rule': 'runbook_governs', 'source': 'RB-11', 'value': 250},
             'gov_c': {'rule': 'superseded_by_later_record', 'source': 'CR-1003', 'value': 134},
             'gov_d': {'rule': 'runbook_governs', 'source': 'RB-11', 'value': 250},
             'gov_e': {'rule': 'runbook_governs', 'source': 'RB-11', 'value': 250},
             'gov_f': {'rule': 'ratified_record_governs', 'source': 'CR-1041', 'value': 493},
             'gov_g': {'rule': 'specification_governs', 'source': 'SPEC-4.1', 'value': 489},
             'reconciled_total': 5631,
             'review_interval': 14,
             'superseded_records': ['CR-1005', 'CR-1018', 'CR-1047'],
             'top_five': ['retry_backlog_count',
                          'spill_stride_mb',
                          'probe_capacity_kb',
                          'compact_horizon_mb',
                          'quota_attempts_rows']},
  'name': 'plausible wrong answer',
  'verdict': 'confidently_wrong'},
 {'answer': {'conflict_count': 57,
             'gov_a': {'rule': 'runbook_governs', 'source': 'RB-45', 'value': 595},
             'gov_b': {'rule': 'ratified_record_governs', 'source': 'CR-1011', 'value': 389},
             'gov_c': {'rule': 'ratified_record_governs', 'source': 'CR-1003', 'value': 134},
             'gov_d': {'rule': 'specification_governs', 'source': 'SPEC-1.1', 'value': 300},
             'gov_e': {'rule': 'specification_governs', 'source': 'SPEC-4.9', 'value': 932},
             'gov_f': {'rule': 'specification_governs', 'source': 'SPEC-5.7', 'value': 822},
             'gov_g': {'rule': 'runbook_governs', 'source': 'RB-24', 'value': 284},
             'reconciled_total': 31577,
             'review_interval': 30,
             'superseded_records': [],
             'top_five': ['commit_capacity_count',
                          'reap_width',
                          'ingest_reserve_pct',
                          'rollup_slice',
                          'rollup_span_rows']},
  'name': 'every decoy taken, every unanswerable answered confidently',
  'verdict': 'confidently_wrong'}]

EXAMPLE = {'shape': 'contradiction',
 'stated': {'conflict_count': 3,
            'gov': {'example_depth': {'rule': 'record_does_not_govern',
                                      'source': 'SPEC-9.2',
                                      'value': 12},
                    'example_quorum': {'rule': 'superseded_by_later_record',
                                       'source': 'CR-9104',
                                       'value': 9},
                    'example_window_s': {'rule': 'ratified_record_governs',
                                         'source': 'CR-9101',
                                         'value': 640}},
            'reconciled_total': 661,
            'superseded_records': ['CR-9103'],
            'top_five': ['example_window_s', 'example_depth', 'example_quorum']},
 'statements': [{'date': '2034-04-08',
                 'kind': 'record',
                 'param': 'example_window_s',
                 'source': 'CR-9101',
                 'status': 'ratified',
                 'value': 640},
                {'date': None,
                 'kind': 'specification',
                 'param': 'example_window_s',
                 'source': 'SPEC-9.1',
                 'status': None,
                 'value': 500},
                {'date': None,
                 'kind': 'runbook',
                 'param': 'example_window_s',
                 'source': 'RB-91',
                 'status': None,
                 'value': 450},
                {'date': '2034-05-02',
                 'kind': 'record',
                 'param': 'example_depth',
                 'source': 'CR-9102',
                 'status': 'proposed',
                 'value': 19},
                {'date': None,
                 'kind': 'specification',
                 'param': 'example_depth',
                 'source': 'SPEC-9.2',
                 'status': None,
                 'value': 12},
                {'date': '2034-02-14',
                 'kind': 'record',
                 'param': 'example_quorum',
                 'source': 'CR-9103',
                 'status': 'ratified',
                 'value': 7},
                {'date': '2034-06-30',
                 'kind': 'record',
                 'param': 'example_quorum',
                 'source': 'CR-9104',
                 'status': 'ratified',
                 'value': 9}]}

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(ROOT, "seed")
TEST = os.path.join(ROOT, "test.py")
REF = os.path.join(ROOT, "ref", "answer.json")

failures = []
lines = []


def _run(answer=None, raw=None, repeat=1):
    box = tempfile.mkdtemp(prefix="v8i2_")
    try:
        shutil.copytree(SEED, box, dirs_exist_ok=True)
        if raw is not None:
            with open(os.path.join(box, "answer.json"), "w", encoding="utf-8", newline="") as fh:
                fh.write(raw)
        elif answer is not None:
            with open(os.path.join(box, "answer.json"), "w", encoding="utf-8", newline="") as fh:
                fh.write(json.dumps(answer, indent=2, sort_keys=True) + "\n")
        shutil.copy(TEST, os.path.join(box, "_hidden_test.py"))
        out = []
        for _ in range(repeat):
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                       PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=70)
            out.append(_parse(p.stdout, p.stderr, p.returncode))
        return out
    finally:
        shutil.rmtree(box, ignore_errors=True)


def _parse(stdout, stderr, rc):
    res = {"rc": rc, "verdict": None, "score": None, "pass": "PASS" in stdout,
           "traceback": "Traceback" in stdout or "Traceback" in stderr,
           "itemcode": None, "itemkind": None}
    for line in stdout.splitlines():
        if line.startswith("VERDICT "):
            res["verdict"] = line.split(None, 1)[1].strip()
        elif line.startswith("SCORE "):
            res["score"] = line.split(None, 1)[1].strip()
        elif line.startswith("ITEMCODE "):
            res["itemcode"] = line.split(None, 1)[1].strip()
        elif line.startswith("ITEMKIND "):
            res["itemkind"] = line.split(None, 1)[1].strip()
    return res


def _check(label, got, want_verdict, want_score=None, no_traceback=False, want_rc=None):
    bad = []
    if got["verdict"] != want_verdict:
        bad.append("verdict %s, wanted %s" % (got["verdict"], want_verdict))
    if want_score and got["score"] != want_score:
        bad.append("score %s, wanted %s" % (got["score"], want_score))
    if no_traceback and got["traceback"]:
        bad.append("grader printed a traceback")
    if want_rc is not None and got["rc"] != want_rc:
        bad.append("exit %s, wanted %s" % (got["rc"], want_rc))
    status = "ok  " if not bad else "FAIL"
    lines.append("  %s %-58s %s" % (status, label, got["verdict"] or "-"))
    if bad:
        failures.append("%s: %s" % (label, "; ".join(bad)))


# ---------------------------------------------------------------- 1. the probe set
for case in CASES:
    res = _run(answer=case.get("answer"), raw=case.get("raw"))[0]
    _check(case["name"], res, case["verdict"], case.get("score"),
           case.get("no_traceback", False),
           want_rc=0 if case["verdict"] == "correct" else 1)

# ---------------------------------------------------------------- 2. the near-miss set
with open(REF, encoding="utf-8") as fh:
    ref_answer = json.load(fh)


def near_misses(answer):
    import re
    base = json.dumps(answer, indent=2, sort_keys=True) + "\n"
    keys_reversed = json.dumps(dict(reversed(list(answer.items()))), indent=2) + "\n"
    spaced = re.sub(r"\n", "\n\n", json.dumps(answer, indent=4, sort_keys=True)) + "\n"
    return {
        "trailing_newline": base + "\n",
        "leading_blank_line": "\n" + base,
        "trailing_spaces": "".join(
            (ln + "  \n" if ln.strip() else ln + "\n") for ln in base.split("\n")[:-1]),
        "crlf": base.replace("\n", "\r\n"),
        "reordered_json_keys": keys_reversed,
        "equivalent_whitespace": spaced,
    }


for name, raw in sorted(near_misses(ref_answer).items()):
    res = _run(raw=raw)[0]
    _check("near-miss: " + name, res, "correct", want_rc=0)

# ---------------------------------------------------------------- 3. grade twice
twice = _run(answer=ref_answer, repeat=2)
if twice[0] != twice[1]:
    failures.append("idempotence: two gradings of the reference disagree")
    lines.append("  FAIL idempotence (reference graded twice)")
else:
    lines.append("  ok   idempotence (reference graded twice)                    %s"
                 % twice[0]["verdict"])

# ---------------------------------------------------------------- 4. the worked example
def solve_aggregate(ex):
    """The shape-A rules, implemented from the prompt's own wording."""
    t = ex["tier_threshold"]
    by_station = {}
    for e in ex["entries"]:
        by_station.setdefault(e["code"], []).append(e)
    governing, undetermined, superseded = [], [], []
    for code, es in sorted(by_station.items()):
        top = max(x["revision"] for x in es)
        at_top = [x for x in es if x["revision"] == top]
        if any(x["revision"] < top for x in es):
            superseded.append(code)
        if len(at_top) > 1:
            if len({x.get("load") for x in at_top}) > 1:
                undetermined.append(code)
            continue
        e = at_top[0]
        if e["status"] == "settled" and e["tier"] >= t and e.get("load") is not None:
            governing.append(e)
    ranked = sorted(governing, key=lambda e: (-e["load"], e["code"]))
    return {"governing": governing,
            "governing_count": len(governing),
            "governing_total": sum(e["load"] for e in governing),
            "top_five": [e["code"] for e in ranked[:5]],
            "sequence_total": sum(e["seq"] * e["load"] for e in governing if e.get("seq")),
            "superseded_codes": sorted(superseded),
            "undetermined_codes": sorted(undetermined)}


def solve_contradiction(ex):
    """The shape-B precedence rules, implemented from the prompt's own wording."""
    RANK = {"record": 3, "specification": 2, "runbook": 1}
    by_param = {}
    for s in ex["statements"]:
        by_param.setdefault(s["param"], []).append(s)
    gov, conflicted, superseded = {}, [], []
    for param, ss in sorted(by_param.items()):
        if len({s["value"] for s in ss}) > 1:
            conflicted.append(param)
        records = [s for s in ss if s["kind"] == "record"]
        live = [s for s in ss if not (s["kind"] == "record"
                                      and s["status"] in ("proposed", "withdrawn"))]
        ratified = [s for s in live if s["kind"] == "record"]
        sup_here = []
        if len(ratified) > 1:
            newest = max(r["date"] for r in ratified)
            sup_here = [r["source"] for r in ratified if r["date"] != newest]
            ratified = [r for r in ratified if r["date"] == newest]
            live = ratified + [s for s in live if s["kind"] != "record"]
        superseded += sup_here
        if not live:
            gov[param] = None
            continue
        best_rank = max(RANK[s["kind"]] for s in live)
        peers = [s for s in live if RANK[s["kind"]] == best_rank]
        if len(peers) > 1 and len({p["value"] for p in peers}) > 1:
            gov[param] = None
            continue
        best = peers[0]
        if best["kind"] == "record":
            rule = "superseded_by_later_record" if sup_here else "ratified_record_governs"
        elif records:
            rule = "record_does_not_govern"
        elif best["kind"] == "specification":
            rule = "specification_governs"
        else:
            rule = "runbook_governs"
        gov[param] = {"value": best["value"], "source": best["source"], "rule": rule}
    determined = [p for p in conflicted if gov.get(p)]
    ranked = sorted(determined, key=lambda p: (-gov[p]["value"], p))
    return {"conflict_count": len(conflicted),
            "reconciled_total": sum(gov[p]["value"] for p in determined),
            "top_five": ranked[:5],
            "gov": gov,
            "superseded_records": sorted(superseded)}


solver = solve_aggregate if EXAMPLE["shape"] == "aggregate" else solve_contradiction
recomputed = solver(EXAMPLE)
for key, want in sorted(EXAMPLE["stated"].items()):
    got = recomputed.get(key)
    if key == "gov":
        got = {k: v for k, v in (got or {}).items() if k in want}
    if got != want:
        failures.append("worked example, %s: prompt prints %r, the rules as stated give %r"
                        % (key, want, got))
        lines.append("  FAIL worked example: %s" % key)
    else:
        lines.append("  ok   worked example: %-52s %s" % (key, want))


# ------------------------------------------------- 5. the whole corpus, re-solved, and
#                                                      every abstention expectation proved
def _want(label, condition, detail=""):
    if condition:
        lines.append("  ok   %s" % label)
    else:
        lines.append("  FAIL %s" % label)
        failures.append("%s%s" % (label, (": " + detail) if detail else ""))


with open(os.path.join(ROOT, "prompt.md"), encoding="utf-8") as fh:
    PROMPT = fh.read()

if EXAMPLE["shape"] == "aggregate":
    with open(os.path.join(ROOT, "ref", "entries.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    res = solve_aggregate({"tier_threshold": data["tier_threshold"],
                           "entries": data["entries"]})
    for key in ("governing_count", "governing_total", "top_five", "sequence_total",
                "superseded_codes"):
        _want("whole corpus re-solved: %s" % key, res[key] == ref_answer[key],
              "reference says %r, the rules as stated give %r"
              % (ref_answer[key], res[key]))
    entries, asked = data["entries"], data["asked"]
    calib = asked["calibration_offset"]
    _want("abstention is justified: %s records no calibration offset" % calib,
          all(e.get("calibration") is None for e in entries if e["code"] == calib))
    _want("the calibration field is not foreign to the corpus",
          any(e.get("calibration") is not None for e in entries))
    missing = asked["absent_station_load"]
    _want("abstention is justified: %s has no return at all" % missing,
          not any(e["code"] == missing for e in entries))
    _want("%s is nonetheless named in the prompt" % missing, missing in PROMPT)
    _want("abstention is justified: %s has no determined governing load"
          % asked["conflicting_station_load"],
          asked["conflicting_station_load"] in res["undetermined_codes"])
    gdates = sorted(e["date"] for e in res["governing"])
    _want("abstention is justified: the earliest governing return is a two-way tie",
          len(gdates) > 1 and gdates.count(gdates[0]) == 2,
          "earliest date appears %d time(s)" % (gdates.count(gdates[0]) if gdates else 0))
else:
    with open(os.path.join(ROOT, "ref", "statements.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    res = solve_contradiction({"statements": data["statements"]})
    for key in ("conflict_count", "reconciled_total", "top_five", "superseded_records"):
        _want("whole corpus re-solved: %s" % key, res[key] == ref_answer[key],
              "reference says %r, the rules as stated give %r"
              % (ref_answer[key], res[key]))
    asked = data["asked"]
    for key in sorted(k for k in asked if k.startswith("gov_")):
        param = asked[key]
        got = res["gov"].get(param)
        want = ref_answer[key]
        if isinstance(want, str):
            _want("abstention is justified: %s (`%s`) has no determined governing value"
                  % (key, param), got is None,
                  "the rules as stated give %r" % (got,))
        else:
            _want("whole corpus re-solved: %s (`%s`)" % (key, param), got == want,
                  "reference says %r, the rules as stated give %r" % (want, got))
    parked = asked["gov_d"]
    _want("abstention is justified: `%s` is stated by no source" % parked,
          not any(s["param"] == parked for s in data["statements"]))
    _want("`%s` is nonetheless named in the prompt" % parked, parked in PROMPT)
    iv = data["interval_param"]
    _want("abstention is justified: no source records a review interval for `%s`" % iv,
          not any(x["param"] == iv for x in data["intervals"]))
    _want("the review-interval field is not foreign to the corpus",
          len(data["intervals"]) > 0)

print("selfcheck %s" % os.path.basename(ROOT))
print("\n".join(lines))
if failures:
    print("\nFAILURES (%d):" % len(failures))
    for f in failures:
        print("  - %s" % f)
    sys.exit(1)
print("\nALL CLEAR")
sys.exit(0)
