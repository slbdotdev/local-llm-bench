#!/usr/bin/env python3
"""v7.6 sweep statistics: the section-3 cost table and the tool-failure table, per sweep.

This is tx_stats.py's per-transcript reader driving a per-sweep aggregation. It does not
re-implement anything the runner or the grader did: correctness, wall and tool calls come
from the rows the runner wrote, and rounds, per-tool calls and failures come from the
transcript each arm C row names for itself.

Usage:
  python3 v76_stats.py v76base.json                 every (arm, label) group in the file
  python3 v76_stats.py v76base.json v76c1.json ...  several files, one table over all groups
  python3 v76_stats.py --slots v76base.json         adds the per-slot table

A group is (arm, label): one sweep. Grouping on the label is why run76.py records it -- a
result file that accumulates sweeps otherwise cannot say which build produced which row.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
from tx_stats import stats  # noqa: E402  -- the per-transcript reader, unchanged
sys.argv = _argv


def group_rows(paths):
    groups = collections.OrderedDict()
    for path in paths:
        for row in json.load(open(path, encoding="utf-8"))["rows"]:
            groups.setdefault((row["arm"], row.get("label", "")), []).append(row)
    return groups


def transcript_stats(rows):
    """Rounds, per-tool calls and failures over the transcripts these rows name.

    Only arm C rows name a transcript. A missing or unreadable one is counted and reported
    rather than silently skipped: a table built from nineteen of twenty transcripts is not
    the sweep, and nothing downstream could tell.
    """
    rounds = calls = 0
    per_tool = collections.Counter()
    fails = collections.Counter()
    fwo = collections.Counter()
    bare = collections.Counter()
    out_tokens = 0
    missing = 0
    for row in rows:
        path = row.get("transcript")
        if not path or not os.path.exists(path):
            missing += 1
            continue
        r, c, f, w, b, o = stats(path)
        rounds += len(r)
        calls += sum(c.values())
        per_tool.update(c)
        fails.update(f)
        fwo.update(w)
        bare.update(b)
        out_tokens += o
    return rounds, calls, per_tool, fails, fwo, bare, out_tokens, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--slots", action="store_true", help="also print the per-slot table")
    ap.add_argument("--tools", action="store_true", default=True)
    a = ap.parse_args()

    groups = group_rows(a.files)

    print("| arm | correct | wall s | tool calls | API rounds | output tokens |")
    print("| --- | --- | --- | --- | --- | --- |")
    summaries = {}
    for (arm, label), rows in groups.items():
        ok = sum(1 for r in rows if r["verdict"] == "correct")
        wall = sum(r["wall_s"] or 0 for r in rows)
        tc = sum(r["tool_calls"] or 0 for r in rows)
        rounds = sum(r["turns"] or 0 for r in rows)
        out = sum(r["out_tokens"] or 0 for r in rows)
        summaries[(arm, label)] = (ok, len(rows), wall, tc, rounds, out)
        name = f"{arm} ({label})" if label else arm
        print(f"| {name} | {ok}/{len(rows)} | {wall:,.0f} | {tc} | {rounds} | {out:,} |")
    print()

    for (arm, label), rows in groups.items():
        caps = [r["task"] for r in rows if r.get("stop_reason") == "wall_cap"]
        bad = [(r["task"], r["verdict"]) for r in rows if r["verdict"] != "correct"]
        print(f"# {arm} ({label}): {len(rows)} rows; wall caps {caps or 'none'}; non-correct {bad or 'none'}")

    if a.slots:
        for (arm, label), rows in groups.items():
            print()
            print(f"## per slot -- {arm} ({label})")
            print("| slot | verdict | wall s | tool calls | rounds | out tokens |")
            print("| --- | --- | --- | --- | --- | --- |")
            for r in sorted(rows, key=lambda r: r["task"]):
                cap = " (wall cap)" if r.get("stop_reason") == "wall_cap" else ""
                print(f"| {r['task']} | {r['verdict']}{cap} | {r['wall_s']:.0f} | {r['tool_calls']} "
                      f"| {r['turns']} | {r['out_tokens']:,} |")

    for (arm, label), rows in groups.items():
        if not any(r.get("transcript") for r in rows):
            # The pi arm keeps no slbh transcript; its per-tool histogram is in the row.
            tools = collections.Counter()
            for r in rows:
                tools.update(r.get("tools") or {})
            if tools:
                print()
                print(f"## tool calls -- {arm} ({label}), from the runner's own pi histogram")
                print("| tool | calls |")
                print("| --- | --- |")
                for name, n in tools.most_common():
                    print(f"| {name} | {n} |")
            continue
        rounds, calls, per_tool, fails, fwo, bare, out, missing = transcript_stats(rows)
        print()
        print(f"## tool failures -- {arm} ({label}); transcripts read {len(rows) - missing}/{len(rows)}, "
              f"rounds {rounds}, completion tokens {out:,}")
        print("| tool | calls | failed | failed with output attached | failed bare |")
        print("| --- | --- | --- | --- | --- |")
        for name, n in per_tool.most_common():
            print(f"| {name} | {n} | {fails[name]} | {fwo[name]} | {fails[name] - fwo[name]} |")
        print(f"| **all** | **{sum(per_tool.values())}** | **{sum(fails.values())}** | "
              f"**{sum(fwo.values())}** | **{sum(fails.values()) - sum(fwo.values())}** |")
        if bare:
            print()
            print("bare failure lines:")
            for text, n in bare.most_common(10):
                print(f"  {n:3d}x {text[:110]}")


if __name__ == "__main__":
    main()
