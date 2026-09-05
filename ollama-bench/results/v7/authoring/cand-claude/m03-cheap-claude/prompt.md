You are working in a snapshot of the `ledger-tap` repository.

The test suite is failing. Run it and fix the library so that it passes:

    PYTHONPATH=src python -m pytest tests

The tests state the behaviour the project wants and they are correct; the defect is in the
library. Fix the defect, do not change the tests, and keep the change as small as it needs to be.

`docs/rounding.md` is authoritative on what the arithmetic is supposed to do and explains why.

Change nothing in this repository except what fixing that defect requires.
