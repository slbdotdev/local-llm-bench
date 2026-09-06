#!/usr/bin/env python3
"""The v7 material-coverage and load-bearing-file gate, read from the bench's own fields.

    python3 results/v7/coverage_gate.py <tag> [<tag> ...]        # gate a scored cell
    python3 results/v7/coverage_gate.py --verify-calibration     # reproduce calibration's numbers
    python3 results/v7/coverage_gate.py --tasks-dir DIR <tag>    # gate candidates, not the suite
    python3 results/v7/coverage_gate.py --json out.json <tag>

plan-2026-09-07.md section 2.2, in full:

  **Material coverage must reach 50% of the candidate's material**, and the trial must touch at
  least **five** of the paths the checker names load-bearing. Peak input is reported beside both
  as the capacity number and is never itself a gate.

The three numbers, and where each comes from:

| number | field | what it is |
| --- | --- | --- |
| coverage | `read_paths` x MANIFEST `files` | **the gate.** Sum of `material_tokens` for the files a trial actually named, over the task's own `material_tokens`. Attributable, and not paddable by a long conversation. |
| coverage (expanded) | `read_paths_expanded` | an **upper bound**, adding the files a directory or glob token named. Reported, never gated: `grep -rn x docs/` pulls matching lines into context, not whole files. |
| peak input | `achieved_fill_prompt_tokens` | the **capacity** diagnostic. It includes the system prompt, the task, prior turns and tool results (calibration section 11), so it is an upper bound on material read and never a lower one. Never `in_tokens`, which sums across turns. |

`LOAD_BEARING` is read out of each task's `test.py` with `ast.literal_eval` — parsed, never
imported and never executed, because a grader is a program that calls `sys.exit`.

`timed_out` and `stop_reason` are printed beside every verdict, because a row can be `correct`
at the timeout (D7-24, calibration section 11).

A task whose manifest predates the `files` map, or a run recorded before `read_paths` existed,
reports coverage as `n/a` rather than as `0`: an absent instrument is not a measurement of
zero, and reading it as one is how a capacity result gets read as a quality one.
"""
import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(BENCH, "results")
SUITE = os.path.join(HERE, "authoring", "suite")
CALIBRATION = os.path.join(HERE, "calibration-2026-09-06.md")

COVERAGE_FRACTION = 0.50        # owner's ruling on section 8.1, 2026-09-07
LOAD_BEARING_TOUCHED = 5        # plan section 2.4, proposed and to be re-derived after sweep 1
LOAD_BEARING_MIN_PATHS = 6
LOAD_BEARING_MIN_HOPS = 3

WINDOW = {"main": {"IQ2_M": 65536, "Q2_K": 65536, "UDQ3KXL": 49152},
          "cheap": {"IQ2_M": 24576, "Q2_K": 24576, "UDQ3KXL": 24576}}


# ---------------------------------------------------------------------------
# reading the task side
# ---------------------------------------------------------------------------

def load_task_dirs(tasks_dirs):
    """slot -> {manifest, load_bearing}. Later directories win, so a candidate can shadow."""
    out = {}
    for root in tasks_dirs:
        if not os.path.isdir(root):
            continue
        for slot in sorted(os.listdir(root)):
            d = os.path.join(root, slot)
            mp = os.path.join(d, "MANIFEST.json")
            if not os.path.exists(mp):
                continue
            with open(mp, encoding="utf-8") as fh:
                man = json.load(fh)
            out[slot] = {"dir": d, "manifest": man,
                         "load_bearing": load_bearing(os.path.join(d, "test.py"))}
    return out


def load_bearing(test_py):
    """`LOAD_BEARING` out of a grader, by parsing it. Never imported: a grader exits."""
    if not os.path.exists(test_py):
        return None
    with open(test_py, encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "LOAD_BEARING":
                try:
                    return ast.literal_eval(node.value)
                except ValueError:
                    return None
    return None


def fold(paths):
    return set((p or "").replace("\\", "/").lower() for p in paths or [])


# ---------------------------------------------------------------------------
# the gate itself
# ---------------------------------------------------------------------------

def gate_run(run, task):
    """One trial's coverage row. Everything here is read out of the record and the manifest."""
    man = task["manifest"] if task else {}
    files = {k.replace("\\", "/").lower(): v for k, v in (man.get("files") or {}).items()}
    material = man.get("material_tokens") or 0
    lb = task.get("load_bearing") if task else None

    has_paths = "read_paths" in run
    read = fold(run.get("read_paths"))
    read_x = fold(run.get("read_paths_expanded"))

    row = {
        "task": run.get("task"), "verdict": run.get("verdict"), "score": run.get("score"),
        "timed_out": run.get("timed_out"), "stop_reason": run.get("stop_reason"),
        "turns": run.get("turns"), "tool_calls": run.get("tool_calls"),
        "out_tokens": run.get("out_tokens"), "tools": run.get("tools"),
        "peak": run.get("achieved_fill_prompt_tokens"), "material": material,
        "files_in_manifest": len(files), "read_n": len(read), "read_expanded_n": len(read_x),
        "instrumented": has_paths and bool(files),
    }
    row["peak_pct_material"] = (round(100.0 * row["peak"] / material, 1)
                                if material and row["peak"] is not None else None)

    if not row["instrumented"]:
        row.update({"coverage_tokens": None, "coverage_pct": None,
                    "coverage_expanded_pct": None, "lb_touched": None,
                    "lb_touched_expanded": None, "lb_paths": len(lb or []),
                    "gate": "n/a", "why": _why_na(has_paths, files, material)})
        return row

    cov_tokens = sum(files.get(p, 0) for p in read if p in files)
    cov_tokens_x = sum(files.get(p, 0) for p in read_x if p in files)
    row["coverage_tokens"] = cov_tokens
    row["coverage_pct"] = round(100.0 * cov_tokens / material, 1) if material else None
    row["coverage_expanded_pct"] = (round(100.0 * cov_tokens_x / material, 1)
                                    if material else None)

    lb_paths = fold(p["path"] for p in (lb or []))
    hops = set(p.get("hop") for p in (lb or []))
    row["lb_paths"] = len(lb_paths)
    row["lb_hops"] = len(hops)
    row["lb_touched"] = len(lb_paths & read)
    row["lb_touched_expanded"] = len(lb_paths & read_x)

    problems = []
    if lb is None:
        problems.append("test.py declares no LOAD_BEARING")
    else:
        if len(lb_paths) < LOAD_BEARING_MIN_PATHS:
            problems.append("LOAD_BEARING has %d paths, the plan requires %d"
                            % (len(lb_paths), LOAD_BEARING_MIN_PATHS))
        if len(hops) < LOAD_BEARING_MIN_HOPS:
            problems.append("LOAD_BEARING carries %d hops, the plan requires %d"
                            % (len(hops), LOAD_BEARING_MIN_HOPS))
    if row["coverage_pct"] is None or row["coverage_pct"] < 100 * COVERAGE_FRACTION:
        problems.append("coverage %s%% is below the %d%% the plan requires"
                        % (row["coverage_pct"], 100 * COVERAGE_FRACTION))
    if lb is not None and row["lb_touched"] < LOAD_BEARING_TOUCHED:
        problems.append("touched %d of %d load-bearing paths, the plan requires %d"
                        % (row["lb_touched"], len(lb_paths), LOAD_BEARING_TOUCHED))
    row["gate"] = "PASS" if not problems else "FAIL"
    row["why"] = "; ".join(problems)
    return row


def _why_na(has_paths, files, material):
    if not has_paths:
        return ("the run record predates read_paths, so coverage is unavailable, "
                "not zero")
    if not files:
        return ("MANIFEST.json carries no `files` map; run "
                "authoring/stamp_manifests.py, then re-run the trial")
    if not material:
        return "MANIFEST.json carries no material_tokens"
    return "uninstrumented"


# ---------------------------------------------------------------------------
# gating scored cells
# ---------------------------------------------------------------------------

def cell_runs(tag):
    p = os.path.join(RESULTS, tag + ".json")
    if not os.path.exists(p):
        raise SystemExit("no such result file: %s" % p)
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    out = []
    for model, rec in sorted(data.items()):
        for run in rec.get("runs", []):
            out.append((model, run))
    return out


def report(tags, tasks_dirs, jsonout=None):
    tasks = load_task_dirs(tasks_dirs)
    rows = []
    print("%-20s %-16s %-7s %-6s %-8s %-8s %-9s %-7s %-5s %-6s %s"
          % ("task", "model", "verdict", "peak", "peak/mat", "cover%", "cover+x%",
             "lb", "to", "stop", "gate"))
    for tag in tags:
        for model, run in cell_runs(tag):
            r = gate_run(run, tasks.get(run.get("task")))
            r["tag"], r["model"] = tag, model
            rows.append(r)
            print("%-20s %-16s %-7s %-6s %-8s %-8s %-9s %-7s %-5s %-6s %s"
                  % (r["task"], model, (r["verdict"] or "-")[:7], r["peak"],
                     _pct(r["peak_pct_material"]), _pct(r["coverage_pct"]),
                     _pct(r["coverage_expanded_pct"]),
                     ("%s/%s" % (r["lb_touched"], r["lb_paths"])
                      if r["lb_touched"] is not None else "n/a"),
                     "yes" if r.get("timed_out") else "no",
                     (r.get("stop_reason") or "-")[:6], r["gate"]))
    bad = [r for r in rows if r["gate"] == "FAIL"]
    na = [r for r in rows if r["gate"] == "n/a"]
    if bad:
        print("\nBELOW THE GATE — a re-author, not a tune (plan section 2.5):")
        for r in bad:
            print("  %-20s %s" % (r["task"], r["why"]))
    if na:
        print("\nNOT MEASURABLE — the instrument is missing, which is not a coverage of zero:")
        for r in na:
            print("  %-20s %s" % (r["task"], r["why"]))
    print("\n%d row(s): %d pass the gate, %d below it, %d not measurable"
          % (len(rows), len(rows) - len(bad) - len(na), len(bad), len(na)))
    if jsonout:
        with open(jsonout, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1)
    return 1 if bad else 0


def _pct(v):
    return "n/a" if v is None else ("%.1f" % v)


# ---------------------------------------------------------------------------
# --verify-calibration: prove the gate reads real fields
# ---------------------------------------------------------------------------

CAL_ROW = re.compile(r"^\|\s*(m\d\d-(?:main|cheap)-\w+)\s*\|(.+)\|\s*$", re.M)


def parse_calibration():
    """The peak / material / peak-vs-material figures calibration-2026-09-06.md printed.

    Two table shapes are parsed and both are checked. Section 1's occupancy table is
    `task | peak | material | peak vs material | peak vs window`; sections 3 and 4 print the
    fifteen-column per-quant table, whose peak, material and two percentages sit in columns
    9 to 12. Rows are keyed by (table heading, task) so a task appearing in six tables is six
    independent checks.
    """
    out = []
    heading = "section 1 occupancy"
    for line in open(CALIBRATION, encoding="utf-8"):
        if line.startswith("###") or line.startswith("## "):
            heading = line.strip().lstrip("#").strip()
            continue
        m = CAL_ROW.match(line)
        if not m:
            continue
        task = m.group(1)
        cells = [c.strip() for c in m.group(2).split("|")]
        cells = [c for c in cells]
        if len(cells) == 4:
            peak, material, pm, pw = cells
        elif len(cells) >= 14:
            peak, material, pm, pw = cells[7], cells[8], cells[9], cells[10]
        else:
            continue
        try:
            out.append({"heading": heading, "task": task,
                        "peak": int(peak.replace(",", "")),
                        "material": int(material.replace(",", "")),
                        "peak_pct": int(pm.strip("*% ")),
                        "window_pct": int(pw.strip("*% "))})
        except ValueError:
            continue
    return out


def tag_for(heading):
    m = re.search(r"tag `([^`]+)`", heading)
    return m.group(1) if m else None


def verify_calibration():
    """Recompute every occupancy figure in the calibration report from the artifacts.

    This is the proof that the gate reads real fields rather than fields it invented: the same
    `achieved_fill_prompt_tokens` and the same `MANIFEST.json` the report was written from,
    read by the gate's own code path, must reproduce the report's own numbers exactly.
    """
    tasks = load_task_dirs([SUITE])
    claimed = parse_calibration()
    if not claimed:
        raise SystemExit("parsed no rows out of %s" % CALIBRATION)

    measured = {}
    for fn in sorted(os.listdir(RESULTS)):
        if not (fn.startswith(("v7cal-", "v7cal2-")) and fn.endswith(".json")):
            continue
        tag = fn[:-5]
        band = tag.split("-")[2]
        quant = tag.split("-")[1]
        by_task = {}
        for _model, run in cell_runs(tag):
            by_task.setdefault(run["task"], []).append(run)
        for task, runs in by_task.items():
            peaks = sorted(r.get("achieved_fill_prompt_tokens", 0) for r in runs)
            peak = peaks[len(peaks) // 2]
            man = tasks.get(task, {}).get("manifest", {})
            mat = man.get("material_tokens", 0)
            win = WINDOW[band][quant]
            measured[(tag, task)] = {
                "peak": peak, "material": mat,
                "peak_pct": round(100.0 * peak / mat) if mat else 0,
                "window_pct": round(100.0 * peak / win),
            }

    bad = 0
    checked = 0
    unmatched = 0
    print("%-34s %-20s %-10s %-10s %s" % ("table", "task", "field", "report", "recomputed"))
    for row in claimed:
        tag = tag_for(row["heading"])
        if tag is None:
            # Section 1's table names no tag; it is the workhorse's own first main-band pass.
            tag = "v7cal-IQ2_M-main"
        key = (tag, row["task"])
        if key not in measured:
            unmatched += 1
            continue
        got = measured[key]
        for field in ("peak", "material", "peak_pct", "window_pct"):
            checked += 1
            if got[field] != row[field]:
                bad += 1
                print("%-34s %-20s %-10s %-10s %s   <== MISMATCH"
                      % (row["heading"][:34], row["task"], field, row[field], got[field]))
    print("\n%d figure(s) checked against the calibration report, %d mismatched, "
          "%d report row(s) had no artifact" % (checked, bad, unmatched))
    if bad == 0 and checked:
        print("\nThe gate reproduces every occupancy figure in calibration-2026-09-06.md from\n"
              "results/v7cal*.json and authoring/suite/*/MANIFEST.json — the same fields it\n"
              "gates a candidate on. Coverage itself is not reproducible for those rows and is\n"
              "reported `n/a`: they were scored before `read_paths` existed.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--tasks-dir", action="append", default=[])
    ap.add_argument("--verify-calibration", action="store_true")
    ap.add_argument("--json", dest="jsonout")
    a = ap.parse_args()
    if a.verify_calibration:
        return verify_calibration()
    if not a.tags:
        ap.error("give a result tag, or --verify-calibration")
    return report(a.tags, a.tasks_dir or [SUITE], a.jsonout)


if __name__ == "__main__":
    sys.exit(main())
