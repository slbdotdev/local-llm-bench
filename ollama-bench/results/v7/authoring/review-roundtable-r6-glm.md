# Review — roundtable.md round-six docs pass (author Luna; reviewer GLM, 2026-09-08)

verdict: ACCEPT WITH FIXES — one clause in the m09 admission row is contradicted by both of its cited passing reviews; everything else in the section checks out exactly.

Scope: only "Round six — admissions and trials (2026-09-08)". Nothing edited, no git writes.

## What was checked and found correct

1. **Paths and commits.** All 16 cited review files exist (r6/review-m02-{glm,opus}-r6d.md, r6/review-m05-{glm,opus}-r6c.md, r6/review-q09-glm-r6d.md, r6/review-q09-opus-r6e.md, cand-{luna/m03,glm/m04,glm/m07,luna/m09}-*/reviews/{glm,opus}-2026-09-08.md, r6/review-m08-opus-r6{b,c}.md). Every one carries verdict: PASS on its leg. All 12 cited commits exist with matching subjects: 2261d86 (m02), faf8d3d (m05), 0c4d7d2 (q09 admitted), cd902fb (q09 shelving lift), d42ca4e (q09 shelved), 4d42aa5+5bf00c8 (m03, glm fixed-build), 403b2be (m04), aad8cf8+522c5ca (m07, specs), 8f57a23 (m09), 8ac61e4 (m08 shelved).
2. **Fix-round summaries.** m02 ✓ (module-side ownership harvest: opus r6 fix line; token-count/rung-0 accounting ~5,200 tokens: opus r6c finding 2; module-over-document verbatim: opus r6d). m05 ✓ (4-file + single-token: glm r6; all four fix actions in opus r6b fix line, confirmed closed in r6c). q09 ✓ (modulo: opus r6b "the graded key needs two modulo terms the seed never states"; qzx: opus r6d; four-file: r5/reviews/q09-main-glm--luna-1.md "4 files, score 12/12 … fails rung 0"; r6e left exactly the two §4 NOTES claims). m03 ✓ (CSV-only: opus 09-07; re-rolled legacy list and LP-07 explicitly foreclosing the date-only bypass: glm 09-08; glm leg on fixed build: 5bf00c8). m04 ✓ (three rung-0 bypasses: opus 09-07 §2; module paths: opus 09-07:146; parser/docstring, 18→19 count, near-miss table: glm 09-08). m07 ✓ (bound_module one-grep rung-0: opus 09-07 finding 1; contradictory module paths: finding 2; both closed: 09-08 reviews, "round two's contradictory module paths are gone"). m08 ✓ (8ac61e4; opus r6c "2 files, score 7/7" watermark intersection; two fix rounds / five reviews consistent with r6/ listing).
3. **Trials table.** m01 10/5, m10 10/5 (r6-accept-tally-final.json), m02 10/8 and m05 10/9 (r6-accept-tally-m05.json), m07 10/8 and q09 10/6 (r6-accept-tally-m07.json), m09 10/10 (r6-accept-tally-m09.json) — all match. m03-main-luna 0 trials (m09 tally), m04-main-glm 0 trials (m07 tally) — PENDING correct; GPU_BUDGET.log shows the m03 step started 19:10:23Z, end PENDING. Wilson 95% recomputed from scratch (z=1.959963985) for all five distinct (k,n): (5,10)→[0.237,0.763], (6,10)→[0.313,0.832], (8,10)→[0.490,0.943], (9,10)→[0.596,0.982], (10,10)→[0.722,1.000] — all five match the table to three decimals.
4. **GPU.** m02 560, m05 896, q09 3096, m09 1055, m07 1771 each match a log END line; m01/m10 shared 6,068 = 1,167 + 4,901 per the log NOTEs; campaign total 13,938 s (3h52m18s) matches the final NOTE verbatim.
5. **Banked caveats.** All three verbatim-supported: q09 r6e notes_claims (asserts ≤9 vs measured 2; "real trailing material" vs blank/`#` padding) and m04 opus 09-08 fix line (byte-perturbed label is actually the wrong-row-count case).

## Finding (the one fix)

**m09-main-luna admission row, clause 4 of the summary — "and varying figure offsets" is false.**
Both cited passing reviews state the opposite about the committed build:
- `cand-luna/m09-main-luna/reviews/glm-2026-09-08.md`: "frames are fixed (ceiling row at line 17 of every doc, ENFORCED_CEILING at line 14 of every module), a mechanical sweep, but it is the intended traversal".
- `cand-luna/m09-main-luna/reviews/opus-2026-09-08.md` fix line: "vary the position of the `ceiling` row … and of `ENFORCED_CEILING` … so the two are no longer at a fixed line offset (17 and 14)" — i.e. the offset variation is recorded as *outstanding, non-blocking* work, not something the fix rounds closed.

Fix: delete "and varying figure offsets" from the m09 row (the remaining three clauses are verbatim-accurate per opus-09-08: definition moved to the glossary, ledger grown to 119 rows so both date routes run past the first screen, `ingest` added as the conforming-date decoy), or replace it with a note that fixed frames at 17/14 stand and offset variation is opus's banked non-blocking suggestion.

## Uncertainty

- "the final r6e review left only two NOTES wording caveats" counts the two required §4 corrections; the r6e review adds an explicitly *optional* §9 nit ("state-dependent relief"). The review's own framing ("correct the two §4 sentences") supports "two", so not counted as a defect.
- The middle of roundtable.md (earlier sections) was truncated in one read pass; per brief those sections are out of scope. Register line for m09 ("REVISE twice, then landed") is consistent with the section.
