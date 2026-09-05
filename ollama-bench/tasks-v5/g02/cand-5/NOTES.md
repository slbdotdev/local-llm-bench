This candidate makes a release-plan repair hard by requiring the solver to reconcile seven catalog shards, a lock snapshot, platform policy revisions, dated alias history, and dependency-first rendering. It uses A4 levers 1 (material held at once), 2 (the tempting wildcard-policy interpretation is wrong), and 3 (canonicalize, validate, close, order, then render in series). The localized defect is that the planner passes `"*"` instead of the requested platform to policy evaluation.

The task is a positive transformation: the correct repair produces a non-empty valid plan for the primary cases. It also contains explicit negative cases where a denied, unavailable, missing, or incomplete target must produce an empty plan.

Reference solution: `ref/releaseplan/` is 248 lines total across 10 Python files, roughly 1,800 output tokens. `prompt.md` is 291 words.

Selfcheck: both prompt examples passed. `test.py` against the reference produced `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0. The pristine seed suite has exactly one failing test before repair (`test_newest_policy_revision_wins`).

A7 checker probes:

| probe | outcome |
| --- | --- |
| correct content, no trailing newline | `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0 |
| correct content, two trailing newlines | `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0 |
| correct content, CRLF line endings | `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0 |
| correct content, one leading blank line | `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0 |
| correct content, trailing spaces on one line | `SCORE 15/15`, `PASS`, `VERDICT correct`, exit 0 |
| reversed output order (prompt fixes order) | `SCORE 14/15`, `FAIL`, `VERDICT confidently_wrong`, exit 1 |
| plausible wrong answer (reversed dependency order) | `SCORE 14/15`, `FAIL`, `VERDICT confidently_wrong`, exit 1 |
| untouched sandbox (pristine seed) | `SCORE 14/15`, `FAIL`, `VERDICT visibly_failed`, exit 1 |

Items 1–5 exposed no checker defect. The conventional empty-sandbox probe was also run: import failure yielded `SCORE 0/15`, `VERDICT visibly_failed`, exit 1, with no traceback.

No known uncertainty.
