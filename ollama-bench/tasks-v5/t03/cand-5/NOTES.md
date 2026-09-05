# cand-5 authoring notes

This is a large-band t03 comprehension variant. It makes the solver hold a repository-sized
body of evidence at once, reconcile current modules with policy, finance, compliance,
operations, tests, and a longer dated history, and reject a plausible emergency request.
It uses A4 levers 1 (more material), 2 (nearby stale/proposed/rejected answers), and 3
(serial scope -> status -> component -> representation reconciliation). It does not rely on
ambiguity: the prompt defines ordinary baseline scope, effective status, field types, units,
and normalization. The tempting stale answer is weekly / 45000 / 30 / 0.70 / team contact /
2034-10-31 / Juniper / RELAY-17; the tempting rejected emergency values include 90, 50000,
and 0.90. The correct answer is positive: an effective ordinary baseline exists and its
eight approved fields are extracted. The separate emergency-override proposition is
negative: MR-42 is not approved or effective, which is the main false-positive trap.

The reference answer is one line and approximately 35 output tokens. The seed is 142739
characters, or 30604 tokens by the mandated 4.664 character/token method, across 37 files.

## A7 checker probes

The prompt does not fix whitespace, line endings, or object member order. All formatting-only
near-misses therefore pass; the order variant is valid because the prompt explicitly says
member order is not significant. The plausible stale/rejected answer is complete and scalar,
so it is classified confidently_wrong. An untouched sandbox is visibly_failed.

- 1. Correct content, no trailing newline — PASS (`SCORE 8/8`, `VERDICT correct`).
- 2. Correct content, two trailing newlines — PASS (`SCORE 8/8`, `VERDICT correct`).
- 3. Correct content, CRLF line endings — PASS (`SCORE 8/8`, `VERDICT correct`).
- 4. Correct content, one leading blank line — PASS (`SCORE 8/8`, `VERDICT correct`).
- 5. Correct content, trailing spaces on one line — PASS (`SCORE 8/8`, `VERDICT correct`).
- 6. Correct content, different member ordering — PASS (`SCORE 8/8`, `VERDICT correct`).
- 7. Plausible but wrong complete answer — PASS probe (`SCORE 0/8`, `VERDICT confidently_wrong`).
- 8. Untouched sandbox — PASS probe (`SCORE 0/8`, `VERDICT visibly_failed`).

No A7 checker defect was found; probes 1-6 were re-run after the initial checker review and
all passed. The checker reads only answer.json and tolerates extra sandbox files.

## Verification

`selfcheck.py`: PASS. `test.py` against `ref/`: `SCORE 8/8`, `PASS`, `VERDICT correct`,
exit 0. No known uncertainty beyond the inherent risk that a model may choose not to read
all of the distributed evidence.
