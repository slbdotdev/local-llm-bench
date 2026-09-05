#!/usr/bin/env python3
"""Build Capacity Planning's limits report (report/limits.csv).

Coverage policy (docs/policy/capacity-report.md): the report covers every
stage in config/manifest.json except the stages on Platform Reliability's
rota. Which stages those are is recorded in exactly one place, the on-call
column of docs/operations.md, so the exclusion set is read from there at
run time rather than hardcoded here.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "config" / "manifest.json"
OPERATIONS_PATH = ROOT / "docs" / "operations.md"
REPORT_DIR = ROOT / "report"
REPORT_PATH = REPORT_DIR / "limits.csv"

EXCLUDED_TEAM = "Platform Reliability"


def on_call_rota(path):
    """Return {stage: on-call team} parsed from the stage table in operations.md."""
    rota = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0] == "stage" or set(cells[0]) <= set("-:"):
            continue  # header row or column-alignment row
        rota[cells[0]] = cells[3]
    return rota


def main():
    stages = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["stages"]
    rota = on_call_rota(OPERATIONS_PATH)

    rows = [
        (stage["name"], stage["limit"], stage["window_s"])
        for stage in stages
        if rota.get(stage["name"]) != EXCLUDED_TEAM
    ]
    rows.sort(key=lambda row: (-row[1], row[0]))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write("stage,limit,window_s\n")
        for name, limit, window_s in rows:
            f.write(f"{name},{limit},{window_s}\n")


if __name__ == "__main__":
    main()
