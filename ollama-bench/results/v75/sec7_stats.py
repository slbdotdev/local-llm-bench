#!/usr/bin/env python3
"""Section 7 numbers: sweep B (unfixed slbh 9bd142a) against arm C (fixed).

Pairs each sweep-B row with its slbh runtime transcript: the run directories
not already named by any other v75 result file, ordered by the transcript's
own first event time (the sweep ran slots sequentially), checked by tool-call
count, which the runner read from the same transcript's headless summary.
"""
import collections
import datetime as dt
import json
import pathlib
import sys

RES = pathlib.Path("/mnt/d/local-llm-bench/ollama-bench/results/v75")
RUNTIMES = pathlib.Path("/mnt/c/Users/slb/.slbh/runtimes")
SWEEP_B_START = dt.datetime(2026, 9, 12, 23, 51, 0).timestamp()

sys.argv = [sys.argv[0]]
sys.path.insert(0, str(RES))
from tx_stats import stats  # noqa: E402

before = json.load(open(RES / "v75r1-before.json"))["rows"]
fixed = [r for r in json.load(open(RES / "v75r1.json"))["rows"] if r["arm"] == "slbh_real"]
fixed_by = {r["task"]: r for r in fixed}

claimed = set()
for f in ("v75r1.json", "v75fix.json", "v75fix-before.json", "v75smoke.json"):
    for r in json.load(open(RES / f))["rows"]:
        t = r.get("transcript")
        if t:
            claimed.add(t.split("\\")[5])


def transcript_of(run):
    hits = list(run.glob("agents/*/sessions/*/transcript.jsonl"))
    return hits[0] if len(hits) == 1 else None


def first_time(tx):
    with open(tx, encoding="utf-8") as fh:
        return json.loads(fh.readline())["time"]


cands = []
for p in RUNTIMES.iterdir():
    if not p.is_dir() or p.name in claimed or p.stat().st_mtime < SWEEP_B_START:
        continue
    tx = transcript_of(p)
    if tx:
        cands.append((first_time(tx), p, tx))
cands.sort()
print(f"sweep B rows: {len(before)}; unclaimed run dirs since sweep B start: {len(cands)}")
for t, p, _ in cands:
    print(f"   {t} {p.name}")
if len(cands) != len(before):
    sys.exit("pairing count mismatch")

calls_total = collections.Counter()
fails_total = collections.Counter()
fwo_total = collections.Counter()
bare_total = collections.Counter()
rounds_total = 0
out_total = 0
per_slot = []
mismatches = 0
for row, (t0, run, tx) in zip(before, cands):
    rounds, calls, fails, fwo, bare, out = stats(tx)
    match = sum(calls.values()) == row["tool_calls"]
    mismatches += not match
    calls_total.update(calls)
    fails_total.update(fails)
    fwo_total.update(fwo)
    bare_total.update(bare)
    rounds_total += len(rounds)
    out_total += out
    per_slot.append((row, tx, rounds, calls, fails, fwo, out, match))
    print(f"{row['task']:16s} {row['verdict']:17s} wall={row['wall_s']:6.1f} calls={row['tool_calls']:3d} "
          f"rounds={len(rounds):4d} out={out:6d} match={match} {run.name} {t0[11:19]}Z")
print(f"pairing mismatches: {mismatches}")

ok = sum(1 for r in before if r["verdict"] == "correct")
wall = sum(r["wall_s"] for r in before)
tc = sum(r["tool_calls"] for r in before)
print()
print("| arm | correct | wall s | tool calls | API rounds | output tokens |")
print("| --- | --- | --- | --- | --- | --- |")
print(f"| slbh, unfixed 9bd142a | {ok}/{len(before)} | {wall:,.0f} | {tc} | {rounds_total} | {out_total:,} |")
fw = sum(fixed_by[r['task']]['wall_s'] for r in before)
ft = sum(fixed_by[r['task']]['tool_calls'] for r in before)
fr = sum(fixed_by[r['task']]['turns'] for r in before)
fo = sum(fixed_by[r['task']]['out_tokens'] for r in before)
fok = sum(1 for r in before if fixed_by[r['task']]['verdict'] == 'correct')
print(f"| slbh, fixed d4b3930, same slots | {fok}/{len(before)} | {fw:,.0f} | {ft} | {fr} | {fo:,} |")

print()
print("| slot | unfixed | fixed |")
print("| --- | --- | --- |")
for row, *_ in per_slot:
    f = fixed_by[row["task"]]
    cap = " (wall cap)" if row["stop_reason"] == "wall_cap" else ""
    fcap = " (wall cap)" if f["stop_reason"] == "wall_cap" else ""
    print(f"| {row['task']} | {row['verdict']}, {row['wall_s']:.0f} s / {row['tool_calls']}{cap} | "
          f"{f['verdict']}, {f['wall_s']:.0f} s / {f['tool_calls']}{fcap} |")

print()
print("| tool | calls | failed | failed with output attached | failed bare |")
print("| --- | --- | --- | --- | --- |")
for name, n in calls_total.most_common():
    print(f"| {name} | {n} | {fails_total[name]} | {fwo_total[name]} | {fails_total[name] - fwo_total[name]} |")
print(f"| **all** | **{sum(calls_total.values())}** | **{sum(fails_total.values())}** | "
      f"**{sum(fwo_total.values())}** | **{sum(fails_total.values()) - sum(fwo_total.values())}** |")
print()
print("bare failure lines:")
for text, n in bare_total.most_common(8):
    print(f"  {n:3d}x {text[:110]}")
print()
print("non-correct rows:")
for row, tx, *_ in per_slot:
    if row["verdict"] != "correct":
        print(f"  {row['task']}: {row['verdict']} score={row['score']} stop={row['stop_reason']} rc={row['rc']}")
        print(f"    grader: {row['grader'][:300]!r}")
        print(f"    transcript: {tx}")
