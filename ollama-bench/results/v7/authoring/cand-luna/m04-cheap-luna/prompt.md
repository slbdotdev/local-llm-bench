# Dispatch release check

Repair the dispatch stage's completed-record state so that the state written by its keyed
expansion operation is spelled `expanded`, and the dispatch state vocabulary contains that same
spelling. Do not alter the tests.

Run the release check after making the change. It imports the package from `src`, so run
it with `src` on the path:

    PYTHONPATH=src python tests/release_check.py

It exits 0 when the check succeeds and non-zero when it does not. Create `report.txt` in
the repository root. Its first line must be exactly `TESTS: pass` when the check succeeds and
exactly `TESTS: fail` when it does not; report what you actually observed, not what you intended.
Leave unrelated files alone.
