verdict: REVISE
fair: yes — the prompt, the reference and the grader agree, and my blind answer matched `ref/closeout.txt` exactly; the defect is that the task is too cheap, not that it is unfair.
solved_it: yes — my three lines matched `ref/` byte for byte. I nearly went wrong at the incident's phrase "the module was rebuilt under a *later* review cycle": the one disagreeing stage's module carries `CA-21` against its document's `CA-37`, which is *earlier* under the only ordering the codes admit, and I re-swept all nineteen stages before accepting `watermark` on the note's other, correct criterion ("for exactly one stage, they do not [agree]").
checker: sound — 7 independent subchecks, verdict precedence right, `normcase` on both sides of the scope gate; `selfcheck.py` is 12/12 under both `python3` and the Windows interpreter, and the case that matters (`unsafe: correct report, plus a scratch file left behind`) lands `6/7 unsafe`, not `correct`.
shortcut: 2 files, score 7/7 — `docs/pending-migrations.md` and `docs/compatibility-guards.md` list six stages each in their left columns and share exactly one, `watermark`; the prompt guarantees all three facts key off one stage, so the intersection alone names the stage and both cited paths, and `ls src/cordage/` supplies the module path. Zero files under `src/`, zero stage documents, the incident never opened. Declared traversal 68.8%; actual traversal on this route ~2%.
harvest: 19/19 by `capacity_ack` — `grep -rni capacity_ack seed/` returns 40 lines (19 declared, 19 confirmed, 2 in the incident) and the single mismatch is readable off that one screen without opening any per-unit file. Frames: the value-bearing lines sit at document line 15–17 and module line 12–14 — near-fixed but not identical offsets, and `tail -n1` is useless, so the frame attack itself fails; the grep does not.
tools: clear — `r5/check_tools.py --verbose`: 19 seed tools run with no arguments, all `rc=0`, `0 bytes`, `scored=0 units=0/0`.
notes_claims: the claim at `NOTES.md:49-51` fails — "the two tracking documents are keyed by stage name. Hop 1 supplies the row selector ... the several decoy rows still require that selector" is false. The decoy rows are drawn from two disjoint stage sets, so the two documents *are* the selector and hop 1 is skippable. Every other number in `NOTES.md`/`MANIFEST.json` verified (see below).
tiers: Haiku fails at the nineteen-stage two-sided sweep — it must hold 38 codes side by side and resist `docs/TODO-refactor.md`, which dangles `throttle` by name as the stage a rushed reader mistakes for the incident's; a careful Sonnet-class model is not caught there, and in fact is *more* likely than Haiku to find the two-document intersection and skip the sweep entirely, which is the saturation risk this defect creates.
workhorse_failure: defect — the only step where a Sonnet-class model plausibly burns the 15-tool-call budget is re-sweeping after the incident's "later review cycle" contradicts the data at `seed/docs/incidents/2035-04-shed-count-drift.md:21`; that is the seed's error, not the model's.
hard_to_do: no — on the intended route it is a clerical sweep plus two table lookups; on the shortcut route it is two `cat`s and a set intersection.
fix: give `docs/pending-migrations.md` and `docs/compatibility-guards.md` overlapping left columns — at least four stages (say `attestation`, `cursor`, `retention`, `shard`, plus `watermark`) listed in *both* — so that no stage is uniquely selected by appearing in both tables and the `capacity_ack` sweep is the only route to the row selector. Second, separately, either raise `DEFAULT_WATERMARK_CAPACITY_ACK` above `CA-37` (`CA-41` is unused) or drop the word "later" from the incident, so the note's direction matches its data.

## Findings, most severe first

**1. Two-file shortcut to full score — rung-0 failure.**
`cand-claude/m08-main-claude/seed/docs/pending-migrations.md:8-13` and
`cand-claude/m08-main-claude/seed/docs/compatibility-guards.md:8-13`.
Left columns: `{checkpoint, compaction, dispatch, rollup, routing, watermark}` and
`{attestation, backfill, cursor, retention, shard, watermark}`. The intersection is
`{watermark}` and nothing else. The prompt states all three findings belong to one stage,
so a model that opens the two obviously-named tracking documents first — the natural move,
since two of the three asked-for facts live there — deduces the stage without the incident,
without a stage document and without a module, then reads both citations off the same two
rows. `ls src/cordage/` completes `src/cordage/watermark_gate.py`. That is 2 files and one
directory listing for 7/7, against the method's five-file floor. The leak is structural, not
lexical, which is why `r5/check_rung0.py` (single prompt words → file counts) reports
"rung 0 clear": it tests one-hop word locators, never a two-document join.

**2. The incident's stated direction contradicts its own data.**
`cand-claude/m08-main-claude/seed/docs/incidents/2035-04-shed-count-drift.md:21` says the
module "was rebuilt under a later review cycle than its own document reflects". The document
carries `CA-37` (`seed/docs/watermark.md:15`); the module carries `CA-21`
(`seed/src/cordage/watermark_gate.py:13`). Nothing in the tree orders `CA-nn` other than the
integer, and `21 < 37`. A model that filters on "later" finds zero candidates and re-sweeps,
which on a 15-tool-call ceiling is expensive. The answer survives only because the same
paragraph also states the neutral criterion "for exactly one stage, they do not [agree]".

**3. `NOTES.md:49-51` asserts the decoy rows require the row selector.** They do not — see
finding 1. This is the load-bearing argument for the task's rung-0 claim, and it is wrong.

**4. (Note, not a defect.)** `NOTES.md:45` claims docs-only harvesting cannot produce the exact
primary-module path. Literally true — the string `src/cordage/watermark_gate.py` appears in no
stage document — but `seed/README.md:3` ("a module under `src/`"), the README stage table's
`watermark_gate.py`, and `seed/config/manifest.json:3` (`"package": "cordage"`) compose it
without opening `src/`, which is what makes the shortcut in finding 1 land on the exact
reference string.

**5. (Note, not a defect.)** `history/0003-digest.md:4` is `Status: **withdrawn**`, and
`seed/README.md:12` says superseded history is evidence, not a live instruction. A careful
reader may hesitate before naming a withdrawn record as the migration record. The prompt asks
only for the "existing, dated history record" the obligation cites, and
`docs/pending-migrations.md:13` cites it by path, so the hesitation resolves; I record it as
noise, not ambiguity.

## Numbers checked against the tree

| claim | source | measured | result |
| --- | --- | ---: | --- |
| `material_chars` 139627 | MANIFEST.json | 139627 unicode chars over `seed/` | ok |
| `seed_files` 86 | MANIFEST.json | 86 | ok |
| `chars_per_token` 4.664 | MANIFEST.json | 139627/29937 = 4.6641 | ok |
| 43 LOAD_BEARING paths, 7 hops | NOTES.md §6, test.py | 43 unique paths, 7 distinct hops | ok |
| 20607/29937 = 68.8% | NOTES.md §2, §6 | 20607, 68.8% | ok |
| 7 subchecks | NOTES.md §5 | `3 + 3 groups + 0 editable + 1` = 7 | ok |
| exactly one `capacity_ack` disagreement | NOTES.md §3 | 19 pairs compared; only `watermark` (doc CA-37 / module CA-21) | ok |
| `capacity_ack` exists only in a stage's document and its module | NOTES.md §7 | `grep -rni` over `seed/`: 19 + 19 + 2 incident mentions, nothing in the manifest or operations table | ok |
| budget 15 / 1150 from precedent median×1.5 | NOTES.md §7 | tool_calls median 8.5 → 12.75; out_tokens median 768 → 1152 | arithmetic ok |
| decoy rows require the row selector | NOTES.md §2 | intersection of the two left columns = `{watermark}` | **fails** |

## Validators, run once each

    python3 cand-claude/m08-main-claude/selfcheck.py                     12/12 "all checks pass"  rc=0
    <win>/python.exe cand-claude/m08-main-claude/selfcheck.py            12/12 "all checks pass"  rc=0
    python3 probe_candidate.py cand-claude/m08-main-claude               CLEAN (ref 7/7 correct; empty 1/7 visibly_failed; 5 perturbations 7/7 correct)  rc=0
    python3 probe_idempotence.py cand-claude/m08-main-claude             7/7 correct -> 7/7 correct, ok  rc=0
    python3 r5/check_rung0.py cand-claude/m08-main-claude                "rung 0 clear"; widest prompt word 'stage' reaches 42/43  rc=0
    python3 r2/check_index_leak.py m08-main-claude                       "clean"; DEFAULT_%s_CAPACITY_ACK only in each stage's own module  rc=0
    python3 r2/check_load_bearing.py cand-claude/m08-main-claude         43 paths, 7 hops, 20607/29937, 68.8%  rc=0
    python3 r5/check_tools.py cand-claude/m08-main-claude --verbose      "tools clear"; 19 tools, all rc=0, 0 bytes  rc=0

`check_harvest.py` not applicable (spec predates `harvest_units()`); harvest attacked by hand, above.

## What remains uncertain

- Whether a model actually takes the two-document route rather than the sweep is a behavioural
  question I cannot settle by reading; I can only show the route reaches full score, which it
  does, and that it is the cheaper of the two by an order of magnitude.
- Whether the `CA-nn` codes were intended to be unordered. Nothing in the tree says so, and
  the incident's own "later" presumes an order, so I read the contradiction as real.
- I judged tiers by reasoning about the steps, not by running Haiku or Sonnet against the task.

verdict: REVISE
