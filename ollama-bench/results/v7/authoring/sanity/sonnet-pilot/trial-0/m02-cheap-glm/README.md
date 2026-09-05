# quartermaster

Small stockroom helpers used by the Workshop team: what is on the shelves,
what has fallen to its reorder point, and the monthly summary the buyers
receive. Python 3, standard library only, no services and no database.

## Layout

    src/quartermaster/   the package
        stock.py         on-hand levels versus reorder points (released)
        report.py        monthly buyer summary (mid-refactor)
    tests/               pytest-style tests, run from the repo root
    config/              reorder_points.json, reviewed quarterly
    data/                inventory.csv (current) and the August stock-take
    docs/                usage, stocking policy, onboarding notes
    scratch/             personal working notes; not part of the package
    history/             short dated notes about changes

## Status

`stock.py` and its tests are stable and released. `report.py` is
mid-refactor: the legacy `render_legacy_summary` entry point is being
replaced by `render_summary`, and `tests/test_report_legacy.py` still pins
the legacy name, so those tests fail until the refactor lands. That is
known and planned; see `scratch/refactor-notes.md` and
`history/2026-07-18-report-refactor-started.md`.

## Running the checks

From the repo root:

    python -m pytest tests/test_stock.py
    python src/quartermaster/stock.py

The stock tests pass on the released code; the second command prints the
current low-stock SKUs, one per line, in inventory file order.

## Ownership

The package is owned by the Workshop team (stockroom systems). The reorder
points themselves are owned by Data Stewardship and reviewed quarterly;
their policy lives in `docs/stocking-policy.md`.
