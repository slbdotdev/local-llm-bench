# Candidate 5 notes

This is the large-band transformation variant. It makes the model reconcile a
versioned project spread across current modules, release configuration, four
importer/replay families, fixture evidence, and a longer superseded history.
The hard levers are A4.1 (much more material held at once), A4.2 (sorting,
raw-counting, broad normalization, or administrative-label leakage is a
plausible-looking wrong answer), and A4.3 (source lifecycle, policy, identity,
arithmetic, and label merging must each feed the next in one ordered fold).
There is no intentional ambiguity or unstated convention.

The correct answer is positive: this is a concrete transformation task, not a
negative “nothing found” comprehension claim.

Measured material (A2 exact character-count snippet): 139923 characters,
30001 tokens at 4.664 characters/token, 109 seed files; band large.

Reference and validation:

- `ref/solution.py`: 66 lines, roughly 750 output tokens (219
  whitespace-delimited Python words)
  (well under the 5,000-token output limit).
- `python3 selfcheck.py`: `selfcheck: PASS (9 examples)`; exit 0.
- checker with `ref/solution.py`: `SCORE 24/24`, `PASS`, `VERDICT correct`;
  exit 0.

A7 shaped near-miss probe (all were run in fresh temporary sandboxes):

- 1. Correct content, no trailing newline: `SCORE 24/24`, `PASS`,
  `VERDICT correct`, exit 0.
- 2. Correct content, two trailing newlines: `SCORE 24/24`, `PASS`,
  `VERDICT correct`, exit 0.
- 3. Correct content, CRLF line endings: `SCORE 24/24`, `PASS`,
  `VERDICT correct`, exit 0.
- 4. Correct content, one leading blank line: `SCORE 24/24`, `PASS`,
  `VERDICT correct`, exit 0.
- 5. Correct content, trailing spaces on one line: `SCORE 24/24`, `PASS`,
  `VERDICT correct`, exit 0.
- 6. Order violation (the prompt fixes order): `SCORE 19/24`, `FAIL`,
  `VERDICT confidently_wrong`, exit 1.

The separate plausible-but-wrong sorted-output answer produced `SCORE 19/24`,
`FAIL`, `VERDICT confidently_wrong`, exit 1. The untouched sandbox produced
`SCORE 0/24`, `FAIL ['import failed: ModuleNotFoundError']`,
`VERDICT visibly_failed`, exit 1, with no traceback. No checker defect was
found in A7 items 1–5, so none required fixing.

Uncertainty: the A6 positive/negative wording is designed for comprehension
tasks; this candidate is a transformation, so “positive” records that it has a
concrete ledger result rather than a yes/no negative claim. Otherwise no known
uncertainty remains.
