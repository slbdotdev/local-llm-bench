#!/usr/bin/env python3
"""Render the v7 calibration tables from the scored artifacts.

    python3 results/v7/summarize_cal.py [tagprefix ...]     # default: v7cal- and v7cal2-

Occupancy is read BEFORE the pass rate, per plan section 7 step 4 and v6's D6-30. A main-band
trial whose peak prompt comes in far below the task's own material size did not exercise the
band, and its row is a capacity result rather than a quality one. `achieved_fill_prompt_tokens`
is the PEAK single-turn input, which is the most context the model ever actually held; `in_tokens`
is the sum across turns and overstates occupancy several-fold.

Nothing here is transcribed by hand: every number comes out of results/<tag>.json and each
task's own MANIFEST.json (D7-23 — a number written down once is a claim about a directory, and
the directory moves).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(BENCH, "results")
SUITE = os.path.join(HERE, "authoring", "suite")

WINDOW = {"main": {"IQ2_M": 65536, "Q2_K": 65536, "UDQ3KXL": 49152},
          "cheap": {"IQ2_M": 24576, "Q2_K": 24576, "UDQ3KXL": 24576}}
VERDICTS = ("correct", "confidently_wrong", "visibly_failed", "unsafe", "unverified_claim")


def manifests():
    out = {}
    for slot in sorted(os.listdir(SUITE)):
        p = os.path.join(SUITE, slot, "MANIFEST.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                out[slot] = json.load(fh)
    return out


def cells(prefixes):
    """(quant, band, tag) -> list of runs, from every results/<prefix>*.json."""
    out = {}
    for fn in sorted(os.listdir(RESULTS)):
        if not fn.endswith(".json") or not any(fn.startswith(p) for p in prefixes):
            continue
        tag = fn[:-5]
        parts = tag.split("-")
        quant, band = parts[1], parts[2]
        with open(os.path.join(RESULTS, fn), encoding="utf-8") as fh:
            data = json.load(fh)
        for model, r in data.items():
            out.setdefault((quant, band, tag, model), []).extend(r.get("runs", []))
    return out


def fmt(runs, man, quant, band):
    lines = []
    lines.append("| task | mode | trials | correct | cw | vf | unsafe | uc | peak prompt | "
                 "material | occ vs material | occ vs window | median wall | turns | stop |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    by_task = {}
    for x in runs:
        by_task.setdefault(x["task"], []).append(x)
    totals = dict.fromkeys(VERDICTS, 0)
    n = 0
    for task in sorted(by_task):
        rs = by_task[task]
        m = man.get(task, {})
        mat = m.get("material_tokens", 0)
        win = WINDOW[band][quant]
        counts = {v: sum(1 for x in rs if x.get("verdict") == v) for v in VERDICTS}
        for v in VERDICTS:
            totals[v] += counts[v]
        n += len(rs)
        peaks = [x.get("achieved_fill_prompt_tokens", 0) for x in rs]
        peak = sorted(peaks)[len(peaks) // 2]
        walls = sorted(x["wall_s"] for x in rs)
        wall = walls[len(walls) // 2]
        turns = sum(x["turns"] for x in rs) / len(rs)
        stops = sorted({x.get("stop_reason") or "-" for x in rs})
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d%% | %d%% | %.0f | %.1f | %s |"
                     % (task, int(task[1:3]), len(rs), counts["correct"],
                        counts["confidently_wrong"], counts["visibly_failed"], counts["unsafe"],
                        counts["unverified_claim"], peak, mat,
                        round(100 * peak / mat) if mat else 0, round(100 * peak / win),
                        wall, turns, ",".join(stops)))
    lines.append("| **total** | | **%d** | **%d** | %d | %d | %d | %d | | | | | | | |"
                 % (n, totals["correct"], totals["confidently_wrong"], totals["visibly_failed"],
                    totals["unsafe"], totals["unverified_claim"]))
    return lines, n, totals


def main():
    prefixes = sys.argv[1:] or ["v7cal-", "v7cal2-"]
    man = manifests()
    grand = {}
    for (quant, band, tag, model), runs in sorted(cells(prefixes).items()):
        print("\n### %s — %s band (`%s`, tag `%s`), %d trials\n" % (quant, band, model, tag, len(runs)))
        lines, n, totals = fmt(runs, man, quant, band)
        print("\n".join(lines))
        g = grand.setdefault(quant, dict.fromkeys(VERDICTS, 0))
        g["n"] = g.get("n", 0) + n
        for v in VERDICTS:
            g[v] += totals[v]
    print("\n### Headline, both bands together\n")
    print("| quant | trials | correct | pass rate | confidently_wrong | visibly_failed | unsafe | unverified_claim |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for quant, g in sorted(grand.items()):
        print("| %s | %d | %d | **%.0f%%** | %d | %d | %d | %d |"
              % (quant, g["n"], g["correct"], 100 * g["correct"] / g["n"] if g["n"] else 0,
                 g["confidently_wrong"], g["visibly_failed"], g["unsafe"], g["unverified_claim"]))


if __name__ == "__main__":
    main()
