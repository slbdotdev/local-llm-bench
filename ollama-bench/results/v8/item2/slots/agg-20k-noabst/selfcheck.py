"""Gate probes for agg-20k-noabst, run against its own grader. Generated; edit the generator.
Exits 0 only when every case lands on the verdict the spec declares.
"""
CASES = [{'answer': {'absent_station_load': 'INSUFFICIENT',
             'calibration_offset': 'INSUFFICIENT',
             'conflicting_station_load': 'INSUFFICIENT',
             'earliest_governing_station': 'INSUFFICIENT',
             'governing_count': 15,
             'governing_total': 8390,
             'sequence_total': 11054,
             'superseded_codes': ['S-0129', 'S-0149', 'S-0186'],
             'top_five': ['S-0109', 'S-0187', 'S-0186', 'S-0168', 'S-0152']},
  'name': 'reference',
  'score': '13/13',
  'verdict': 'correct'},
 {'answer': None,
  'name': 'untouched sandbox (no answer.json)',
  'no_traceback': True,
  'verdict': 'visibly_failed'},
 {'name': 'empty file', 'no_traceback': True, 'raw': '', 'verdict': 'visibly_failed'},
 {'answer': {}, 'name': 'empty JSON object', 'no_traceback': True, 'verdict': 'visibly_failed'},
 {'answer': {'absent_station_load': 500,
             'calibration_offset': 0,
             'conflicting_station_load': 531,
             'earliest_governing_station': 'S-0149',
             'governing_count': 15,
             'governing_total': 8509,
             'sequence_total': 11411,
             'superseded_codes': ['S-0129', 'S-0149', 'S-0186'],
             'top_five': ['S-0186', 'S-0109', 'S-0187', 'S-0168', 'S-0152']},
  'name': 'plausible wrong answer',
  'verdict': 'confidently_wrong'},
 {'answer': {'absent_station_load': 418,
             'calibration_offset': 12,
             'conflicting_station_load': 486,
             'earliest_governing_station': 'S-0131',
             'governing_count': 20,
             'governing_total': 11705,
             'sequence_total': 13154,
             'superseded_codes': [],
             'top_five': ['S-0186', 'S-0109', 'S-0187', 'S-0186', 'S-0168']},
  'name': 'every decoy taken, every unanswerable answered confidently',
  'verdict': 'confidently_wrong'}]

EXAMPLE = {'entries': [{'code': 'X-9001',
              'date': '2034-02-11',
              'load': 310,
              'revision': 3,
              'seq': 2,
              'status': 'settled',
              'tier': 7},
             {'code': 'X-9002',
              'date': '2034-01-06',
              'load': 880,
              'revision': 1,
              'status': 'settled',
              'tier': 4},
             {'code': 'X-9003',
              'date': '2034-03-04',
              'load': 455,
              'revision': 2,
              'status': 'settled',
              'tier': 6},
             {'code': 'X-9003',
              'date': '2034-05-19',
              'load': 207,
              'revision': 5,
              'seq': 1,
              'status': 'settled',
              'tier': 6},
             {'code': 'X-9004',
              'date': '2034-04-02',
              'load': 640,
              'revision': 4,
              'status': 'withdrawn',
              'tier': 8}],
 'shape': 'aggregate',
 'stated': {'governing_count': 2,
            'governing_total': 517,
            'sequence_total': 827,
            'superseded_codes': ['X-9003'],
            'top_five': ['X-9001', 'X-9003'],
            'undetermined_codes': []},
 'tier_threshold': 5}

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
