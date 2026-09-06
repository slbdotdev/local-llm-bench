#!/usr/bin/env python3
"""Prove pibench's new `read_paths` attribution on a synthetic event stream. CPU only.

    python3 results/v7/probe_read_paths.py [<candidate-dir>]

plan-2026-09-07.md section 2.5 requires two things of `read_paths` and this covers the first:
that the attribution itself is right — an exact file token is credited, a directory or glob
token is credited only to the expanded upper bound, a flag is never a path, an absolute
sandbox path is made relative, and a Windows backslash path is normalised. It feeds
`pibench.record_read_paths` events shaped every way pi could plausibly shape them, because
the plan forbids guessing the argument key: the function scans every string the event carries
and reports the keys it saw in `tool_arg_keys`, so the second requirement — one live run that
reproduces a cell of `results/v7cal-IQ2_M-main.json` and checks the field against that
record's `tools` histogram — is a run and not a re-parse, and it is step 0 of
`results/v7/run_gpu_round.sh`.

Exit 0 when every case attributes exactly what it should.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, BENCH)

import pibench                                        # noqa: E402

SANDBOX = "/tmp/pib_abcdef"

MATERIAL = {
    "files": {
        "docs/glossary.md": 900,
        "docs/operations.md": 400,
        "docs/policy-records/pr-0148-ceilings.md": 700,
        "src/harrow/drain_store.py": 500,
        "src/harrow/lineage_flow.py": 550,
        "config/manifest.json": 300,
        "data/migration-ledger.csv": 250,
        "readme.md": 200,
    },
    "dirs": set(),
}
for _rel in MATERIAL["files"]:
    _parts = _rel.split("/")
    for _i in range(1, len(_parts)):
        MATERIAL["dirs"].add("/".join(_parts[:_i]))


def attribute(ev):
    paths, expanded, keys = set(), set(), {}
    pibench.record_read_paths(ev, MATERIAL, SANDBOX, paths, expanded, keys)
    return sorted(paths), sorted(expanded), keys


CASES = [
    # (name, event, exact paths expected, expanded-only paths expected)
    ("read tool, plain relative path",
     {"type": "tool_execution_start", "toolName": "read",
      "arguments": {"path": "docs/glossary.md"}},
     ["docs/glossary.md"], []),

    ("read tool under a different argument key",
     {"type": "tool_execution_start", "toolName": "read",
      "input": {"file_path": "src/harrow/drain_store.py"}},
     ["src/harrow/drain_store.py"], []),

    ("read tool with an absolute sandbox path",
     {"type": "tool_execution_start", "toolName": "read",
      "arguments": {"path": SANDBOX + "/config/manifest.json"}},
     ["config/manifest.json"], []),

    ("windows backslash path",
     {"type": "tool_execution_start", "toolName": "read",
      "arguments": {"path": "docs\\policy-records\\PR-0148-ceilings.md"}},
     ["docs/policy-records/pr-0148-ceilings.md"], []),

    ("bash cat of two files",
     {"type": "tool_execution_start", "toolName": "bash",
      "arguments": {"command": "cat docs/operations.md data/migration-ledger.csv"}},
     ["data/migration-ledger.csv", "docs/operations.md"], []),

    ("bash grep with a flag that is not a path",
     {"type": "tool_execution_start", "toolName": "bash",
      "arguments": {"command": "grep -n 'ceiling' ./docs/glossary.md"}},
     ["docs/glossary.md"], []),

    ("bash recursive grep over a directory: expanded only",
     {"type": "tool_execution_start", "toolName": "bash",
      "arguments": {"command": "grep -rn ceiling docs/"}},
     [], ["docs/glossary.md", "docs/operations.md",
          "docs/policy-records/pr-0148-ceilings.md"]),

    ("bash glob: expanded only",
     {"type": "tool_execution_start", "toolName": "bash",
      "arguments": {"command": "wc -l src/harrow/*.py"}},
     [], ["src/harrow/drain_store.py", "src/harrow/lineage_flow.py"]),

    ("nested argument payload",
     {"type": "tool_execution_start", "toolName": "read",
      "toolCall": {"function": {"arguments": {"paths": ["readme.md", "docs/operations.md"]}}}},
     ["docs/operations.md", "readme.md"], []),

    ("a string that names nothing in the tree",
     {"type": "tool_execution_start", "toolName": "bash",
      "arguments": {"command": "python -c 'print(1)'"}},
     [], []),
]


def main():
    bad = 0
    print("%-46s %-8s %s" % ("case", "exact", "expanded"))
    all_keys = {}
    for name, ev, want_exact, want_expanded_only in CASES:
        exact, expanded, keys = attribute(ev)
        for k, v in keys.items():
            all_keys[k] = all_keys.get(k, 0) + v
        want_expanded = sorted(set(want_exact) | set(want_expanded_only))
        ok = exact == sorted(want_exact) and expanded == want_expanded
        if not ok:
            bad += 1
        print("%-46s %-8s %s%s" % (name, len(exact), len(expanded), "" if ok else "   <== WRONG"))
        if not ok:
            print("      exact    got %s want %s" % (exact, sorted(want_exact)))
            print("      expanded got %s want %s" % (expanded, want_expanded))
    print("\ntool_arg_keys seen across the synthetic stream: %s" % sorted(all_keys))
    print("%d case(s), %d wrong" % (len(CASES), bad))
    if bad:
        return 1
    print("\nread_paths attribution is correct on every shape probed. The live half of plan "
          "section 2.5\nis step 0 of results/v7/run_gpu_round.sh and needs the GPU.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
