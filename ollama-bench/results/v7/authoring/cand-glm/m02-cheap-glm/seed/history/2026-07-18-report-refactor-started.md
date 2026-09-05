# 2026-07-18 - report.py refactor started

The buyer summary is being moved from reading the CSV itself to taking
in-memory rows (see scratch/refactor-notes.md for the plan). The legacy
entry point stays until the buyers have run one cycle on the new summary;
tests/test_report_legacy.py will fail until then, which is expected and is
not a stock.py problem.
