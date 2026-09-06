#!/usr/bin/env python3
"""The v7 suite statistic: pass probability with its spread, over at least three trials.

    python3 results/v7/tally_trials.py                       # the accepted suite
    python3 results/v7/tally_trials.py --tasks-dir DIR       # some other directory of tasks
    python3 results/v7/tally_trials.py --tag v7r5-fill-a     # add a tag to the allowlist
    python3 results/v7/tally_trials.py --json out.json
    python3 results/v7/tally_trials.py --list-tags           # what is on disk, and what counts

Owner's ruling, 2026-09-06 (campaign 2026-09-10):

  > report pass probability with its spread and the confidently-wrong rate over at least three
  > trials [...] no single-trial number is ever reported as a task property.

So this file replaces `k/n` as the campaign's headline. It reads **every** workhorse results
JSON under `results/`, keeps the trials that were run against the current build of each suite
task (see "Which tags count" below), and reports per task and for the suite:

* **trials, passes, pass probability** — `correct` over trials;
* a **Wilson 95% score interval** on that probability. Wilson rather than the normal
  approximation because n is 3 to 9 and p is often 1.0, where the normal interval is `[1, 1]`
  and says a task that has never been failed can never be failed. Wilson has no such degenerate
  case: 5 of 5 reads 1.000 [0.566, 1.000], which is the honest statement that five trials
  cannot distinguish a 60% task from a perfect one;
* **confidently wrong**, **visibly failed** and **unsafe** counts, because a wrong answer
  delivered with confidence is the failure this benchmark exists to find and it is not the same
  event as running out of context;
* and beside every row, as **diagnostics that gate nothing** (owner's ruling on the coverage
  question, 2026-09-06, plan section 2.2 as amended): mean **coverage**, mean **expanded
  coverage** and mean **peak input**, computed by `coverage_gate.py`'s own `gate_run` so there
  is one implementation of those three numbers and not two.

The suite line is the **mean of the per-task pass probabilities**, not passes over all runs.
They differ whenever the tasks carry different trial counts, and the mean of the task
probabilities is the one that answers "what fraction of this suite does the model pass",
because a task measured nine times is not worth three tasks measured three times. Its interval
is the Wilson interval on the pooled counts, reported as the spread of the suite number, and
the per-task spread is what says which rows are actually pinned down.

## Which tags count

A trial only measures a task if it was run against **that build** of the task. Round four
replaced one task outright and rebuilt others, so the round-two calibration tags
(`v7cal-*`, `v7cal2-*`) are excluded by default: they are one and three trials against an
earlier suite, every task they cover already has five or more trials from `v7r4cal-*`, and
mixing them would silently mingle two builds. That exclusion is a decision, so it is written
here, printed by `--list-tags`, and reversible with `--tag`.
"""
import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(BENCH, "results")
SUITE = os.path.join(HERE, "authoring", "suite")

sys.path.insert(0, HERE)
import coverage_gate as CG          # noqa: E402

WORKHORSE = "IQ2_M"

# tag prefix -> why it counts. A tag counts when it starts with one of these.
COUNTED = {
    "v7r4cal-": "round-four calibration: five trials per accepted task, the current build",
    "v7r4-gate-": "round-four acceptance cells, run against the candidate directories",
    "v7r3-gate-": "round-three acceptance sweep, one trial per candidate",
    "v7r3-rep-": "round-three repeats, three trials per candidate",
    "v7r2-gate": "round-two acceptance sweep and its repeats",
    "v7r5-": "round five: fills, candidate cells and the 48k context-pressure cell",
}
# tag prefix -> why it does not. Reversible with --tag.
EXCLUDED = {
    "v7cal-": "round-two calibration, one trial against an earlier build of the suite",
    "v7cal2-": "round-two repeats, three trials against an earlier build of the suite",
    "v7r4-early-": "round-four early cell, run against candidates that were later revised",
}
# a tag that measures something other than the 64k/24k workhorse pair is never folded in
SEPARATE = {"v7r5-48k": "the context-pressure cell: 48k, reported beside the 64k number, "
                        "never merged into it"}


def wilson(k, n, z=1.959963985):
    """Wilson score interval, the 95% one. Returns (lo, hi), or (None, None) for n = 0."""
    if not n:
        return None, None
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def counted(tag, extra):
    if tag in extra:
        return True, "named with --tag"
    for pre, why in SEPARATE.items():
        if tag.startswith(pre):
            return False, why
    for pre, why in EXCLUDED.items():
        if tag.startswith(pre):
            return False, why
    for pre, why in COUNTED.items():
        if tag.startswith(pre):
            return True, why
    return False, "not a tag this statistic knows about"


def all_tags():
    out = []
    for p in sorted(glob.glob(os.path.join(RESULTS, "v7*.json"))):
        out.append(os.path.basename(p)[:-5])
    return out


def collect(slots, extra_tags, want_tags=None):
    """slot -> list of (tag, model, run), for the workhorse only."""
    rows = {s: [] for s in slots}
    used, skipped = {}, {}
    for tag in all_tags():
        ok, why = counted(tag, extra_tags)
        if want_tags is not None:
            ok = tag in want_tags
            why = "named explicitly"
        if not ok:
            skipped[tag] = why
            continue
        with open(os.path.join(RESULTS, tag + ".json"), encoding="utf-8") as fh:
            data = json.load(fh)
        hit = 0
        for model, rec in sorted(data.items()):
            if WORKHORSE not in model:
                continue
            for run in rec.get("runs", []):
                t = run.get("task")
                if t in rows:
                    rows[t].append((tag, model, run))
                    hit += 1
        if hit:
            used[tag] = "%s (%d run%s)" % (why, hit, "" if hit == 1 else "s")
        else:
            skipped[tag] = "counted, but holds no run of a task in this suite"
    return rows, used, skipped


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(v, w=5, d=1):
    return ("%*.*f" % (w, d, v)) if v is not None else "%*s" % (w, "n/a")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-dir", default=SUITE)
    ap.add_argument("--tag", action="append", default=[],
                    help="fold an extra tag in, overriding the exclusions above")
    ap.add_argument("--only-tags", action="append", default=[],
                    help="use exactly these tags and no others (for a before/after cut)")
    ap.add_argument("--min-trials", type=int, default=3)
    ap.add_argument("--json", dest="jsonout")
    ap.add_argument("--list-tags", action="store_true")
    a = ap.parse_args()

    if a.list_tags:
        for tag in all_tags():
            ok, why = counted(tag, a.tag)
            print("%-28s %-8s %s" % (tag, "counts" if ok else "skipped", why))
        return 0

    slots = sorted(d for d in os.listdir(a.tasks_dir)
                   if os.path.isdir(os.path.join(a.tasks_dir, d)))
    tasks = CG.load_task_dirs([a.tasks_dir])
    rows, used, skipped = collect(slots, a.tag,
                                  set(a.only_tags) if a.only_tags else None)

    print("tasks-dir: %s" % a.tasks_dir)
    print("tags folded in:")
    for tag, why in sorted(used.items()):
        print("  %-28s %s" % (tag, why))
    print()

    out, under = [], []
    for slot in slots:
        trials = rows[slot]
        n = len(trials)
        verdicts = [r.get("verdict") for _t, _m, r in trials]
        k = verdicts.count("correct")
        lo, hi = wilson(k, n)
        cov = [CG.gate_run(r, tasks.get(slot)) for _t, _m, r in trials]
        row = {
            "slot": slot, "trials": n, "passes": k,
            "p": (k / n) if n else None, "lo": lo, "hi": hi,
            "confidently_wrong": verdicts.count("confidently_wrong"),
            "visibly_failed": verdicts.count("visibly_failed"),
            "unsafe": verdicts.count("unsafe"),
            "unverified_claim": verdicts.count("unverified_claim"),
            "coverage_pct": mean([c["coverage_pct"] for c in cov]),
            "coverage_expanded_pct": mean([c["coverage_expanded_pct"] for c in cov]),
            "peak": mean([c["peak"] for c in cov]),
            "tags": sorted({t for t, _m, _r in trials}),
        }
        out.append(row)
        if n < a.min_trials:
            under.append(row)

    print("%-20s %6s %6s %6s  %-16s %4s %4s %4s   %6s %6s %7s"
          % ("task", "trials", "passes", "p", "wilson 95%", "cw", "vf", "uns",
             "cover%", "cov+x%", "peak"))
    for r in out:
        span = ("[%.3f, %.3f]" % (r["lo"], r["hi"])) if r["lo"] is not None else "n/a"
        print("%-20s %6d %6d %6s  %-16s %4d %4d %4d   %6s %6s %7s"
              % (r["slot"], r["trials"], r["passes"],
                 ("%.3f" % r["p"]) if r["p"] is not None else "n/a", span,
                 r["confidently_wrong"], r["visibly_failed"], r["unsafe"],
                 fmt(r["coverage_pct"]), fmt(r["coverage_expanded_pct"]),
                 fmt(r["peak"], 7, 0)))

    n_tot = sum(r["trials"] for r in out)
    k_tot = sum(r["passes"] for r in out)
    cw_tot = sum(r["confidently_wrong"] for r in out)
    ps = [r["p"] for r in out if r["p"] is not None]
    mean_p = mean(ps)
    lo, hi = wilson(k_tot, n_tot)
    cwlo, cwhi = wilson(cw_tot, n_tot)

    print()
    print("suite: %d tasks, %d trials, %d passes" % (len(out), n_tot, k_tot))
    print("  mean pass probability      %.3f   (mean of the %d per-task probabilities)"
          % (mean_p, len(ps)) if mean_p is not None else "  mean pass probability n/a")
    print("  pooled pass rate           %.3f   Wilson 95%% [%.3f, %.3f]  (%d/%d)"
          % (k_tot / n_tot, lo, hi, k_tot, n_tot) if n_tot else "  pooled n/a")
    print("  confidently-wrong rate     %.3f   Wilson 95%% [%.3f, %.3f]  (%d/%d)"
          % (cw_tot / n_tot, cwlo, cwhi, cw_tot, n_tot) if n_tot else "")
    print("  visibly failed %d, unsafe %d, unverified_claim %d"
          % (sum(r["visibly_failed"] for r in out), sum(r["unsafe"] for r in out),
             sum(r["unverified_claim"] for r in out)))
    print("  diagnostics, gating nothing: mean coverage %s%%, expanded %s%%, peak input %s"
          % (fmt(mean([r["coverage_pct"] for r in out])).strip(),
             fmt(mean([r["coverage_expanded_pct"] for r in out])).strip(),
             fmt(mean([r["peak"] for r in out]), 7, 0).strip()))

    if under:
        print()
        print("BELOW %d TRIALS — the ruling forbids reporting these as task properties:"
              % a.min_trials)
        for r in under:
            print("  %-20s %d trial(s)" % (r["slot"], r["trials"]))

    if a.jsonout:
        with open(a.jsonout, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"tasks": out, "tags_used": used, "tags_skipped": skipped,
                                 "suite": {"tasks": len(out), "trials": n_tot,
                                           "passes": k_tot,
                                           "mean_pass_probability": mean_p,
                                           "pooled_pass_rate": (k_tot / n_tot) if n_tot else None,
                                           "wilson95": [lo, hi],
                                           "confidently_wrong": cw_tot,
                                           "confidently_wrong_rate":
                                               (cw_tot / n_tot) if n_tot else None,
                                           "confidently_wrong_wilson95": [cwlo, cwhi]}},
                                indent=1) + "\n")
    return 1 if under else 0


if __name__ == "__main__":
    sys.exit(main())
