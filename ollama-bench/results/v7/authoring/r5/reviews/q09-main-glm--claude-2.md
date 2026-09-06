verdict: REVISE
fair: yes — I solved it from `prompt.md` alone before opening `ref/` and hit all eight values
  exactly (4658/7710/8040/11064/6084/6822/10034/9920); every rule is stated plainly and nothing
  is a puzzle or a judgement call. I nearly went wrong three times and the page caught me each
  time: I read `rebase` as "add the stage's basis" until line 244's "does not adjust the figure
  but sets it", which now matters twice rather than once; I nearly built the walk backwards,
  because `previous` names the *predecessor* and the successor is found by asking who seals
  against me (line 225); and I reached for each page's `limit` row before lines 25-28 ruled the
  assembler's numbers out. The stale 612 in `docs/settlement-summary-2036-q2.md` is ruled out at
  lines 3 and 84-86. Confirmed by measurement that no prompt word greps to exactly one load-
  bearing file: `carryover` reaches 2 (log + procedure), `chain`/`columns`/`rows` reach 2
  (procedure + viewer). The previous review's one-hop breach is fixed.
checker: sound — all fifteen `selfcheck.py` cases pass and `probe_candidate.py` is CLEAN; the
  case I re-ran by hand is "walk stops after entry 25, report filed short" at 3/12
  `confidently_wrong`, and all five whitespace perturbations of a correct answer score 12/12.
harvest: 38/40 by `close` — `grep -rni -A4 close docs/ src/` puts all 38 stated applied figures
  on screen, stage keyed by the file path, and it finishes the answer: with the procedure and the
  log it graded **SCORE 12/12, PASS, VERDICT correct**, run not estimated. No vocabulary is even
  needed. Every balance sits on line **42** of its page and is that file's last line; every
  take-back sits on line **90** of its module and is that file's last line, so
  `tail -n1 docs/*.md src/kestrel/*.py` harvests 19+19 with no token at all, as does
  `grep -rnE '(\*\*[0-9]{4}\*\*|^[A-Z_]+ = 1[0-9]{3}$)' docs/ src/` (38 hits, no false
  positives). The six-way rotation of labels, wordings and constant names is cosmetic because it
  sits inside an identical frame: `## Balance at the review` is byte-identical on **19 of 19**
  pages, and the three-line comment ending `no other line anywhere repeats it` is byte-identical
  in **19 of 19** modules, four lines above the constant. `check_harvest.py` misses both because
  its frame measure only scores tokens it derives from `prompt.md`, the roster and the keys, and
  neither `balance` nor `close` is one; the checker's own note ("38 of 40 stated values are
  digits:4, one shape regex reaches them with no vocabulary at all") is the whole story, and it
  buys everything, not a little. Residual pattern in the figures themselves: sorted, the 19
  balances step by a repeating (64,24,64,24,24) cycle from 1620 and the 19 take-backs by a
  repeating (28,16,16) cycle from 1130, and each stage's rank in its sorted band is exactly
  `5*i mod 19` and `7*i mod 19` in manifest order — both verified for all 19. All 38 figures are
  therefore a closed form generable from about eight observed pages, which is the same class of
  defect as the old `1200 + 40*i`, one inference deeper. The author's claim of "two disjoint
  jittered bands with no arithmetic progression" is false as built.
declaration: honest — `harvest_units()` now declares the figure each entry *applies*, one entry
  per datum, `path` pointing at the page or module that states it; the two derived units are the
  two rebase bases (3394, 3230), which are sums by construction and are disclosed. The wrong-
  quantity defect of the first review is fixed and the measure now bites: H1=0.000 H2=0.000
  H3=0.000 H4=0.175, widest shared frame `second copy` over 7 units.
shortcut: 2 files, score 12/12 — `docs/handbook/settlement-procedure.md` (the rules) and
  `data/settlement-log.csv` (the rows), plus the one grep above. No per-stage file opened and
  `config/manifest.json` not needed: every module's name is its stage's name plus a suffix
  (`watermark_store`, `checkpoint_view`, `attestation_view`), so the grep's own path is the
  stage. Run in a copy of the seed against `test.py`: `SCORE 12/12`, `PASS`, `VERDICT correct`,
  rc 0. `NOTES.md` §9's measured claim of five files is wrong by three, and the shortcut is not
  four but two — the same two as the first review, on a cheaper token. A second, independent
  two-file run is described under `shape:` and also scored 12/12.
notes_claims: two fail. §2: "`previous` is the only artifact of order the log carries, and the
  only thing that orders it" — false, measured: I **deleted the `previous` column outright**,
  ordered the 40 sealed rows by their position in the file alone, and scored 12/12. §2 states the
  hole itself one sentence earlier ("Filing order is a stride permutation of the chain") and then
  asserts the opposite conclusion. §9's "five files opened ... AT the five-file floor" is false
  (two), as is its "the greps' yield still has to be walked in the chain's own order to score
  anything" (it does not, twice over). §4's "the widest single token reaches 4 of 19 stages" is
  true of the rotated labels and false of the material: two byte-identical frames reach 19 of 19
  each. Every *arithmetic* claim verifies: 290 lines, `## Replay rules` at 204, viewer 269 lines
  and 10,198 chars with the opening entry at char 10,135, log 5,948 chars over 43 rows with the
  opening row at line 41 / char 5,387, sweep 26,112 of 34,783 = 75.1%, 42 paths and 6 hops, H4's
  widest frame 7 units, the order-free sum of all forty contributions 19,586, and the sorted-by-
  identifier and as-filed replays both missing 8 of 8.
tiers: Haiku fails at entry 22 — the mid-chain `rebase` (`sc-119`, checkpoint) *sets* the figure
  to the stage's basis rather than adding to it, and the rule saying so is at line 244, forty
  lines below a section heading that is itself at line 204; a model that adds is wrong at
  `figure_after_25` through `figure_final` while looking confident, and the same slip at entry 1
  is wrong at all eight. A careful Sonnet-class model reads to line 246 and is not caught. The
  40 lookups and 40 additions do not separate the tiers: the material is a CSV, a fixed-position
  last line and a fixed-position last line, so a fifteen-line script does the whole replay.
tools: `tools/settlement_status.py` prints 10,198 bytes containing all 43 rows with entry,
  status, date, kind, stage, actor and `seals against`, plus the resolved opening entry — the
  entire selection half of the chain in one command with nothing opened. `check_tools.py` scores
  it `scored=0 units=0/40` and passes it, correctly, because it prints no figure; it is the same
  finding as the first review, unchanged, and it is not by itself fatal since it reprints a file
  the solver reads anyway and the procedure sanctions resolving the opener either way.
shape: **not intact — entry 22 (`sc-119`) is reachable with zero prior entries, and I tested
  `figure_final` (entry 40, `sc-135`) against it.** Three measurements. (1) The two original
  attacks are dead and the revision earns that: replaying in id-sorted order matches **0 of 8**
  keys, as-filed order matches **0 of 8**, and **0 of 2,000** random shuffles of all forty
  contributions reaches 9,920. (2) But a `rebase` *sets*, so adding a second one cut the chain
  instead of lengthening it. Per-entry perturbation shows `figure_after_25/30/35/final` depend on
  entries **22-25, 22-30, 22-35, 22-40** and on **nothing before entry 22**: `figure_final`
  depends on 19 of 40 entries, where before the revision it depended on 39 of 39. Entry 22's own
  value, 3230, is `carried(checkpoint) + absorb(checkpoint)` and needs no prior work at all, and
  the mid-chain rebase is identifiable with one grep and no walk — exactly two rows have kind
  `rebase`, and the one whose `previous` is non-empty is the later one. Starting from 3230 and
  summing the 18 following entries in **2,000 random orders** hits 9,920 **2,000 times out of
  2,000**, entries 1-21 never touched. The same holds inside every segment: each of the eight
  keys is `(nearest preceding rebase basis) + an order-free sum`, 0/1000 mismatches at each. No
  step ever consumes the previous step's *value*; the only serial thing is selection. (3) And the
  selection is free too. The chain order is a pure function of a sealed row's position in the
  file: sort the 40 sealed rows by `(position mod 3 mapped 1,2,0 ; then descending position)` and
  you get the link walk **exactly**, all 40, verified by equality. I built a report from the log
  with the `previous` column deleted and each figure taken from its file's last line — no link
  walked, no token used, no manifest — and it scored **SCORE 12/12, PASS, VERDICT correct**.
  `LOAD_BEARING` calls `data/settlement-log.csv` "the only artifact carrying the chain"; the
  chain is carried by the row layout, and the shuffle went into the identifiers instead of into
  the rows.
hard_to_do: no — the volume is real and the reading is honest, but the anti-harvest mechanism
  buys nothing: it rotates six labels inside two byte-identical frames at two fixed line numbers,
  so the 38 lookups collapse to one grep, and the 40 ordered steps collapse to a sort on row
  position plus four order-free sums. What is left that Sonnet would not do in one script is
  reading to line 244, and that is one line, not forty steps.
fix: rewrite `data/settlement-log.csv` and the two figure frames together. (a) Permute the log's
  **rows** with a real shuffle and assert at build that no affine or stride map from row index
  reproduces the chain — the current layout is a stride-3 reverse traversal and is the whole
  order for free. (b) Delete the second `rebase` and make the order genuinely load-bearing by
  giving one kind an applied figure that is a function of the running figure — e.g. a `clamp`
  entry that sets the figure to `min(figure, stage basis)`, or a `relief` that subtracts
  `min(take-back, figure)` — so that no segment is a commutative sum and `probes()` can assert
  that a shuffle of any segment misses; a `rebase` can never do this, because a set truncates the
  chain rather than extending it. (c) Break the frame: put each stage's balance and constant at a
  different line offset in its file, never last, with no sentence, heading or comment shared by
  more than about four stages, and draw the 38 figures independently at random rather than from
  two regularly-stepped bands indexed by a prime stride.
