# Onboarding notes - workshop stockroom systems

Welcome. This is a small, plain repository; five minutes here saves an
afternoon of guessing.

## Where things live

- `src/quartermaster/` - the package. `stock.py` (the low-stock check) is
  stable and released. `report.py` (the buyer summary) is mid-refactor.
- `tests/` - pytest-style tests. The stock tests pass; the legacy report
  tests are expected to fail until the report refactor lands.
- `config/reorder_points.json` - the reviewed reorder points. Updated at
  the quarterly review; the review notes are under `history/`.
- `data/inventory.csv` - the current shelf figure, refreshed by the Friday
  count. `data/stocktake-2026-08.csv` is the August full stock-take, kept
  for reference only.
- `docs/` - usage, the stocking policy, the count procedure and these
  notes.
- `scratch/` - personal working space: notes, half-written ideas, drafts.
  Nothing in `scratch/` is load-bearing, nothing there is imported by the
  package, and files there appear and disappear without ceremony.
- `history/` - short dated notes about changes worth remembering.

## Conventions

Python 3, standard library only, four-space indent, docstrings on every
public function. Tests run from the repo root. The current inventory file
is the only shelf figure the code reads; older counts stay where they are
for reference.
