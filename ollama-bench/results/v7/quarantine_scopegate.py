#!/usr/bin/env python3
"""Move the three rows invalidated by the Windows-only scope-gate defect (D7-31) out of the
scored artifact and into a quarantine file, so the cell can be re-run over the repaired
graders and the artifact holds only valid rows.

    python3 results/v7/quarantine_scopegate.py

v6 set the precedent with `results/v6/quarantine-Q2_K-64k-t03-contaminated.json` (D6-34): a
trial that measured something other than what it claims to measure is quarantined with its
reason beside it, never silently deleted and never left in the denominator.

pibench resumes per `(task, trial)`, so removing a row is exactly what makes it re-run.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE))
TAG = os.path.join(RESULTS, "v7cal-IQ2_M-main.json")
OUT = os.path.join(HERE, "quarantine-IQ2_M-main-scopegate.json")
SLOTS = {"m02-main-luna", "m05-main-luna", "m08-main-luna"}
REASON = ("VERDICT unsafe produced by a scope gate that compares a normcased file set against "
          "an un-normcased expected set; on Windows normcase lowercases, so the gate fired on "
          "every sandbox including the reference's. Proven by grading each candidate's own "
          "reference under the Windows interpreter (results/v7/probe_scope_gate.py). D7-31.")


def main():
    with open(TAG, encoding="utf-8") as fh:
        data = json.load(fh)
    moved = []
    for model, r in data.items():
        keep = []
        for x in r["runs"]:
            if x["task"] in SLOTS:
                moved.append(dict(x, model=model, quarantine_reason=REASON))
            else:
                keep.append(x)
        r["runs"] = keep
    if not moved:
        print("nothing to quarantine; already done")
        return
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"reason": REASON, "rows": moved}, fh, indent=1)
    with open(TAG, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    print("quarantined %d row(s) to %s" % (len(moved), os.path.basename(OUT)))
    for x in moved:
        print("  %s %s score=%s" % (x["task"], x["verdict"], x["score"]))


if __name__ == "__main__":
    main()
