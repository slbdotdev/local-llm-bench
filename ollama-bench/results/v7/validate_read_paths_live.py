#!/usr/bin/env python3
"""The live half of plan section 2.5's validation of `read_paths`. Reads a scored artifact.

    python3 results/v7/validate_read_paths_live.py <tag> [--task m09-main-glm]

plan-2026-09-07.md section 2.5 requires, before any candidate is gated on the new field:

  > one validation run reproduces a cell of `results/v7cal-IQ2_M-main.json` and checks the new
  > field against that record's `tools` histogram; the stored records hold no raw events, so
  > the check is a re-run and not a re-parse.

This is the checker for that re-run. It is CPU-only — it reads the JSON the re-run produced —
and it is step 0 of `run_gpu_round.sh`, which is what performs the re-run itself.

What it checks, per trial:

1. the record carries `read_paths`, `read_paths_expanded` and `tool_arg_keys` at all;
2. `tool_arg_keys` is non-empty, which is the plan's "argument key read off one live event
   stream and never guessed" — the keys are printed, and the one that carried the paths is
   then a fact in the artifact rather than an assumption in the code;
3. every path in `read_paths` is a real file in that task's own `MANIFEST.json` files map;
4. `read_paths` is a subset of `read_paths_expanded`;
5. the counts are consistent with the `tools` histogram: a trial with file-reading tool calls
   (`read`, `bash`, `grep`, `glob`, or any tool whose name contains `read`/`cat`/`grep`) must
   have attributed at least one path, and a trial with no tool calls at all must have
   attributed none. A read-only count undercounts traversal — `m09-main-glm`'s first pass
   carried nine `bash` calls, one `write` and no `read` — so `bash` counts here.

A failure of 5 with a non-empty `tool_arg_keys` means the attribution is wrong and the gate
must not be believed. A failure of 1 means the re-run did not use the patched pibench.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(BENCH, "results")
SUITE = os.path.join(HERE, "authoring", "suite")

READERS = ("read", "cat", "grep", "glob", "bash", "shell", "ls", "find")


def manifest_files(task, dirs):
    for root in dirs:
        p = os.path.join(root, task, "MANIFEST.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return {k.replace("\\", "/").lower(): v
                        for k, v in (json.load(fh).get("files") or {}).items()}
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--tasks-dir", action="append", default=[])
    a = ap.parse_args()
    dirs = a.tasks_dir or [SUITE]

    path = os.path.join(RESULTS, a.tag + ".json")
    if not os.path.exists(path):
        print("no such result file: %s" % path)
        return 2
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    problems = []
    n = 0
    all_keys = {}
    print("%-20s %-16s %-6s %-6s %-7s %-9s %s"
          % ("task", "model", "tools", "calls", "paths", "expanded", "in manifest"))
    for model, rec in sorted(data.items()):
        for run in rec.get("runs", []):
            n += 1
            task = run.get("task")
            files = manifest_files(task, dirs)
            has = all(k in run for k in
                      ("read_paths", "read_paths_expanded", "tool_arg_keys"))
            if not has:
                problems.append("%s: the record has no read_paths — the re-run did not use "
                                "the patched pibench" % task)
                continue
            paths = [p.replace("\\", "/").lower() for p in run["read_paths"]]
            expanded = [p.replace("\\", "/").lower() for p in run["read_paths_expanded"]]
            keys = run.get("tool_arg_keys") or {}
            for k, v in keys.items():
                all_keys[k] = all_keys.get(k, 0) + v
            tools = run.get("tools") or {}
            calls = run.get("tool_calls") or 0

            unknown = [p for p in paths if p not in files]
            if unknown:
                problems.append("%s: read_paths names %d path(s) that are not in the "
                                "manifest: %s" % (task, len(unknown), unknown[:3]))
            if not set(paths) <= set(expanded):
                problems.append("%s: read_paths is not a subset of read_paths_expanded" % task)
            if not keys and calls:
                problems.append("%s: %d tool calls and an empty tool_arg_keys — the event "
                                "shape is not what the scanner walks" % (task, calls))
            readerish = sum(v for k, v in tools.items()
                            if any(w in k.lower() for w in READERS))
            if readerish and not expanded:
                problems.append("%s: %d file-reading tool call(s) attributed no path at all "
                                "(tools=%s)" % (task, readerish, tools))
            if not calls and expanded:
                problems.append("%s: no tool calls but %d attributed paths"
                                % (task, len(expanded)))
            print("%-20s %-16s %-6d %-6d %-7d %-9d %s"
                  % (task, model, len(tools), calls, len(paths), len(expanded),
                     "%d/%d" % (len(paths) - len(unknown), len(files))))

    print("\ntool_arg_keys observed on the live stream: %s"
          % json.dumps(dict(sorted(all_keys.items())), sort_keys=True))
    if problems:
        print("\nPROBLEMS — do not gate a candidate on read_paths until these are fixed:")
        for p in problems:
            print("  - " + p)
        print("\n%d trial(s), %d problem(s)" % (n, len(problems)))
        return 1
    print("\n%d trial(s) checked, no problems. read_paths is validated against a live event "
          "stream\nand the gate may be read (plan section 2.5)." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
