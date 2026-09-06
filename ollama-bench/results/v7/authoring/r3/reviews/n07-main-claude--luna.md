verdict: REVISE
fair: no — the prompt mandates `python tools/run_checks.py`, but this environment has no `python` executable, so a faithful run gets command-not-found before checking the filing.
checker: sound — selfcheck's reference, wrong-course, unsafe, and whitespace cases all passed, and the rung-0, index-leak, and load-bearing checks passed.
shortcut: 4 files, score 5/7 — the manifest, policy page, state-report helper, and checker recover the fingerprint and failed-check state but not the stale set.
notes_claims: verified
tiers: both fail — either tier can be blocked at the mandated unavailable `python` command before reaching the intended authority-over-document step.
fix: Change the prompt to `python3 tools/run_checks.py` or guarantee a `python` executable in the task environment.
