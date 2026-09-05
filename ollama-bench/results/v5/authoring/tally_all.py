#!/usr/bin/env python3
"""Per-task, per-arm pass/verdict tally across every graded trial of a round.

Usage: python3 tally_all.py <round-dir> [<round-dir> ...]
Reports pass rate and confidently-wrong rate, which is the headline instrument
(plan section 6) and outranks pass rate.
"""
import json, os, sys

for rd in sys.argv[1:]:
    print(f"\n=== {rd} ===")
    for arm in sorted(d for d in os.listdir(rd) if os.path.isdir(os.path.join(rd, d))
                      and d not in ("suite", "prompts") and not d.startswith("suite-")):
        trials = sorted(t for t in os.listdir(os.path.join(rd, arm)) if t.startswith("trial-"))
        rows = {}
        for t in trials:
            p = os.path.join(rd, arm, t, "results.json")
            if not os.path.exists(p):
                continue
            for task, r in json.load(open(p)).items():
                rows.setdefault(task, []).append(r)
        if not rows:
            continue
        tot = cw = ok = 0
        print(f"-- {arm}")
        for task in sorted(rows):
            rs = rows[task]
            p = sum(1 for r in rs if r.get("pass"))
            c = sum(1 for r in rs if r.get("verdict") == "confidently_wrong")
            tot += len(rs); ok += p; cw += c
            print(f"   {task}  {p}/{len(rs)} pass" + (f"   {c} confidently_wrong" if c else ""))
        print(f"   TOTAL {ok}/{tot} = {100.0*ok/tot:.1f}%   confidently_wrong {cw}/{tot} = {100.0*cw/tot:.1f}%")
