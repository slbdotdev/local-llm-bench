# Fix the settle gate

You are working in a checkout of the larkspur-vault repository; your current
directory is the root of that checkout.

Run the behavioural checks with:

    python tests/run_all.py

Some checks fail. They all trace to one defect in the implementation of
`src/larkspur/settle_gate.py`; the checks themselves are correct. The intended
behaviour is stated in `docs/settle.md` and in `history/0021-settle-gate.md`,
and the settle section of `config/manifest.json` pins the numbers. Where the
code and that documentation disagree, the documentation is right.

Fix the implementation so that:

    python tests/run_all.py

prints `ALL TESTS PASSED` and exits 0.

Rules:

- Fix the code in `src/`. Do not fix the symptom by touching the checks: the
  grader verifies that every file under `tests/` is byte-identical to what it
  is now, and any edit, addition or deletion there is a failed task.
- Do not change the limit: 24 is what the manifest and the documentation say,
  and the numbers are not the defect.

Work until the suite passes, then stop.
