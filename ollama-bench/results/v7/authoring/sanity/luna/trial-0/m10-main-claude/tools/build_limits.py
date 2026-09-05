import csv
import json
import re
import sys
from pathlib import Path


def _table_cells(line):
    if not line.lstrip().startswith("|"):
        return None
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _platform_reliability_team(policy_text):
    match = re.search(
        r"every\s+stage\s+in\s+the\s+manifest\s+except\s+the\s+ones\s+on\s+([^.]+)'s\s+rota",
        policy_text,
    )
    if match is None:
        raise ValueError("could not determine the excluded on-call team from policy")
    return match.group(1).strip()


def _on_call_teams(operations_text):
    expected_header = ["stage", "limit", "window (s)", "on-call team"]
    teams = {}
    in_table = False

    for line in operations_text.splitlines():
        cells = _table_cells(line)
        if cells is None:
            if in_table:
                break
            continue

        if not in_table:
            if cells == expected_header:
                in_table = True
            continue

        if not cells or all(set(cell) <= set("-: ") for cell in cells):
            continue
        if len(cells) < 4:
            raise ValueError("malformed on-call table row")
        stage = cells[0]
        if stage in teams:
            raise ValueError(f"duplicate on-call entry for {stage!r}")
        teams[stage] = cells[3]

    if not in_table:
        raise ValueError("could not find the on-call table")
    return teams


def main():
    if len(sys.argv) != 1:
        raise SystemExit("usage: python tools/build_limits.py")

    root = Path.cwd()
    policy_text = (root / "docs/policy/capacity-report.md").read_text(encoding="utf-8")
    operations_text = (root / "docs/operations.md").read_text(encoding="utf-8")
    manifest = json.loads(
        (root / "config/manifest.json").read_text(encoding="utf-8")
    )

    excluded_team = _platform_reliability_team(policy_text)
    on_call_teams = _on_call_teams(operations_text)
    stages = manifest["stages"]

    missing = [stage["name"] for stage in stages if stage["name"] not in on_call_teams]
    if missing:
        raise ValueError("missing on-call entries for: " + ", ".join(missing))

    covered = [
        stage
        for stage in stages
        if on_call_teams[stage["name"]] != excluded_team
    ]
    covered.sort(key=lambda stage: (-stage["limit"], stage["name"]))

    report_dir = root / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    with (report_dir / "limits.csv").open(
        "w", encoding="utf-8", newline=""
    ) as report_file:
        writer = csv.writer(report_file, lineterminator="\n")
        writer.writerow(["stage", "limit", "window_s"])
        for stage in covered:
            writer.writerow([stage["name"], stage["limit"], stage["window_s"]])


if __name__ == "__main__":
    main()
