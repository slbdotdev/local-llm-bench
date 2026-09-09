REVISE

GLM-family admission review of the rebuilt `m08-main-glm` (v7 round 7). Method and shape
conventions taken from `r6/BRIEF-q09-reauthor.md` and `r6/REVIEW-METHOD-q09.md`, read whole
first. Blind: I did not see the author's transcript and opened no `reviews/` directory, no
`r5/reviews/`, no other candidate, nothing under `suite/`. No GPU, no network, no git. I
touched only this report file (plus throwaway copies under `/tmp/m08fire` and
`/mnt/c/Users/slb/AppData/Local/Temp/m08rev`, both scratch, one since deleted).

## What I checked

1. The four owner-ruled failure classes: does a BUILD-TIME assertion exist in the spec for
   each, and does it FIRE when the thing it asserts is perturbed in a throwaway copy.
2. `python3 authoring/r5/stamp_checks.py` from `results/v7/` root.
3. Windows leg (spot-check; seat already verified it).
4. Graded the reference deliverable, one empty-sandbox probe, and an adversarial sweep of my
   own design, all under the Windows interpreter for verdicts.
5. NOTES.md claim-by-claim against the tree.

Before anything: I re-built the candidate from the pinned spec into `/tmp` and diffed —
identical to the shipped tree except the grader docstring's spec-module name (an artifact of
my throwaway loader), so the candidate on disk is exactly what `r5/specs/m08_main_glm.py`
builds. `BUILD OK tokens=35485 in_band=True lb=15`; MANIFEST: mode 9, main, 35485 tokens,
97 files — in the 29,000–36,000 band.

## Fire tests (throwaway copies under /tmp/m08fire, built via `r5.common.build`)

Base copy builds clean; each perturbation is a one-line patch:

- **F1, class 1 — corrupt one `previous` link in the written CSV** (handbook-only walk must
  then diverge): `BUILD FAILED ... f1.py, line 272, in _assert_shape / assert procedure ==
  _replay(ordered, figures)`. The handbook-only replay assertion fires. PASS as closure.
- **F5, class 1 — log position order == chain order** (unshuffle the CSV): `BUILD FAILED ...
  line 250 ... assert actual_positions != [(a * i + b) % 20 ...]` — the identity affine map
  was caught. All seven field sorts, `position mod k` (k=2..8) and the a=-64..64 affine scan
  are asserted in-spec. PASS as closure.
- **F2, class 2 — plant a shared 4-char substring across two labels**: `BUILD FAILED ...
  line 297 ... assert not (lg & rg)`. Label bigrams, roster-tag bigrams, and stripped
  value-frames (≤4) are all asserted. PASS as closure.
- **F4, class 4 — flatten the offset distribution** (fixed top/tail for every folio):
  `BUILD FAILED ... line 290 ... assert len(set(top_offsets)) >= 12 ...`. The uniqueness
  (`max(count) <= 1`) and never-last-line asserts sit right behind it; F6 (figure moved to the
  last line) fired at `line 288 ... max(eof_offsets.count ...) <= 1`. PASS as closure.
- **F3, class 3 — add a sixth-file shortcut** (a `docs/quick-reference.md` written by the
  overlay carrying all six graded `key: value` lines): **`BUILD OK tokens=35510 in_band=True
  lb=15` — the build does NOT fail.** The class-3 closure is not in the spec. It lives
  post-build in `r5/check_rung0.py`, which does catch it, cleanly: `! B: one file assembles
  every scored value at once: ['docs/quick-reference.md']`. So the property holds on the
  shipped candidate and is gated at admission, but the owner ruling demands a build-time
  assertion in the spec, and the mandated fire test ("confirm the build fails") does not
  fire. **This is the REVISE defect.** Concrete fix: in `facts()` after `expect` is computed,
  assert over the built seed that no file contains more than one expect value (equivalently:
  every checkpoint/final value occurs nowhere under `seed/` — I verified today that this
  holds), and/or that no prompt-vocabulary token reaches every `load_bearing()` path (the
  spec knows both). One assert, same style as the other three.

## Independent solve and attacks (my own code, written from prompt+handbook only)

- My replay of handbook constants + linked walk + folio figure pairs reproduced `ref/`
  exactly: opening 271828 / ck05 970686 / ck10 159440 / ck15 623445 / ck20 940009 / final
  940009. Fairness finding: none.
- Order attacks, all miss the final: sorts by rid/previous/card/mult/bias/cw/rw
  (319738/283087/340626/854291/929381/919728/282500), position mod k k=2..8, affine a·i+b
  a∈[-64,64] b∈[0,19] (zero hits), position-sorted replay with `previous` ignored (907761).
- Arithmetic attacks: 80 per-row perturbations (mult, bias, signal, pulse × 20 rows) all
  change the final; 18 contiguous segments × 5 shuffles = 90 shuffled-segment replays, 0 hit
  the segment exit. No commutative segment; chain intact end to end.

## Adversarial sweep of my own design (beyond the battery)

Over the shipped seed, declared figures = the 40 folio values:

- Fixed-line sweep for a *declared* figure, folios and then all 97 seed files: best yield
  **1/40** (line 5). Nothing a fixed-line sweep can use above ~1/40.
- `tail -n1` over every seed file: **0/40** declared figures; no figure is last-line.
- Best single prompt-token grep putting a declared figure *line* on screen: **0/40** (no
  prompt word co-occurs with a figure line). Widest prompt token reaching figure-bearing
  files: `evidence`, 20 of 97 files, 14 of 15 load-bearing (misses `records/sequence.csv`) —
  the traversal, not a shortcut.
- Shape regexes: bare `key: digits` reaches 40/40 folio lines (that is the folio traversal —
  still needs order and params; check_harvest reports it as the ungated digits:4 shape note);
  6-digit state-shaped and CSV-row-shaped regexes reach **0/40**.
- Leakage: `970686 / 159440 / 623445 / 940009` occur nowhere under `seed/`; `271828` occurs
  only in the handbook as the stated opening. Full score needs handbook + CSV + all 20
  folios = 22 files; no ≤5-file path exists in the artifact.
- Widest byte-identical value-frame (value stripped): 1; all 40 top offsets and 40 EOF
  offsets distinct; widest shared label fragment across the 20 folio labels: 1 character.

## Grading (Windows interpreter, `/mnt/c/Users/slb/scoop/apps/python/current/python.exe`)

Sandbox laid out the way `selfcheck.py` does it (grader as `_hidden_test.py`):

- Reference deliverable: `SCORE 10/10 / PASS / VERDICT correct`.
- Empty sandbox: `SCORE 1/10 / VERDICT visibly_failed` — clean.
- `selfcheck.py` under the Windows interpreter: all checks pass, rc 0 (matches the report's
  both-interpreters claim). Windows leg spot-check confirms the seat's result; I did not
  doubt it further.

## Checker battery and stamp

From `results/v7/authoring/`, once each, all rc 0: `selfcheck.py` (10/10 cases),
`probe_candidate.py` (CLEAN), `probe_idempotence.py` (ok), `r5/check_rung0.py` (0 failing;
"no prompt word reaches every load-bearing file; the widest, 'evidence', reaches 14 of 15"),
`r5/check_index_leak.py` (0 leak), `r5/check_load_bearing.py` (15 paths / 15 hops, 4,869 lb
tokens, 13.7%), `r5/check_harvest.py --verbose` (harvest clear, H1=0.000 H2=0.000 H3=0.050
H4=0.000, 40 units / 40 distinct / 0 derived), `r5/check_tools.py --verbose` (tools clear,
17 tools, 0 scored values printed).

`python3 authoring/r5/stamp_checks.py` from `results/v7/`: **every m08-main-glm row is ok**
(selfcheck ok, probe_candidate CLEAN, and m08 included in the passing round-wide rows:
measure_material, stamp_manifests --check, probe_idempotence, stage_gate_suite, probe_scope_gate
4/4 correct + 4/4 breach-fired under the Windows interpreter, probe_read_paths 10/10).
Four rows failed, all out of scope, named:

1. `probe_coverage_gate.py` — the 3 unexpected verdicts are `m02-main-claude`,
   `m05-main-claude`, `m08-main-claude` ("targeted" wanted FAIL, got PASS); other candidates,
   not m08-main-glm (which is not yet in the gate-suite).
2. `coverage_gate.py --verify-calibration` — 38/300 mismatches, all on in-flight
   `q27-UDQ3KXL` / `m09-main-glm` calibration rows; zero m08-main-glm mentions.
3. `validate_all.py` — crashes with `KeyError: 'cheap24'` (harness `BANDS` gap) before
   reporting anything; run alone on this slot it says `m08-main-glm ... ok ok ok ok OK`.
4. `run_gpu_round.sh` (no `--go`) — dry-run PREFLIGHT FAILED; no GPU in this review session.

## NOTES.md honesty

Every claim checked against the tree: mode-9/band/sweep figures match MANIFEST and the build
report (35,490 of 35,485 tokens, 100.0%, generator rounding as across the round); "15
load-bearing hops = procedure, ordering, ruling, twelve folio-figure hops" matches
check_load_bearing; the near-miss probe scores (10/10, visibly_failed, 9/10 ×2, 3/10,
whitespace 10/10 ×5) all reproduce in selfcheck; the sort/sum claim in ¶2 is confirmed by my
own attacks (every field sort misses, shuffled segments miss); "build assertions ... replay
the procedure, reject field/index/affine order shortcuts, perturb every row, reject shuffled
segments, inspect figure offsets and frames" — all present and fire-tested. No false or
unverifiable claim found. The rebuild report's numbers likewise check out, with one nuance
the report itself does not hide but should state as a limitation: closure 4's "rung-0"
bullet is enforced by `r5/check_rung0.py` at the admission gate, not by an in-spec assert —
the exact gap the fire test exposed.

## Verdict

**REVISE.** The artifact is sound and honestly documented; the defect is closure coverage.
One specific defect: class 3 ("no file-only path to full score under five files") has no
build-time assertion in `r5/specs/m08_main_glm.py` — a planted one-file shortcut builds
clean (`BUILD OK`) and is caught only post-build by `r5/check_rung0.py`. Per the ruling and
the fire-test standard ("a build that cannot fail is a REVISE"), add the in-spec assert
proposed above, rebuild, and re-run the F3 fire test; classes 1, 2 and 4 already close
correctly and need no further work. No other defects found; every other measured property
of the candidate passed first-hand verification.
