verdict: REVISE
fair: yes — I solved it from `prompt.md` alone before opening `ref/` and hit all eight
  expected values exactly; every rule I needed is stated plainly in the procedure page, and
  nothing is a puzzle, an encoding or a judgement call. I nearly went wrong three times and
  the material caught me each time: I reached for the filed 2036-Q2 summary's 612 as an
  opening balance until the prompt's "not any summary previously filed in the tree" and the
  procedure's replay-never-carried-forward section stopped me; I first read `rebase` as "set
  to the stage's carried figure" and had to read two lines further to line 245 for "carried
  figure plus its absorb figure"; and I guessed the module filename from the stage name
  before checking `config/manifest.json`'s name-to-module map, which would have failed on
  `watermark` → `watermark_store`. All three are stated facts I skimmed past, not ambiguities.
checker: sound — my independently derived report scored 12/12 `correct`; the walk truncated
  after entry 25 scores 3/12, keys out of prompt order score 3/12, the stale-summary answer
  scores 11/12 `confidently_wrong`, and all five whitespace perturbations pass.
harvest: 39/39 by `units` — `grep -rni units docs/ src/` prints 45 lines, 39 of which are
  exactly the 19 `carried` table rows and the 19 `ABSORB_UNITS = NNNN` lines, with the
  stage keyed by the file path; the two narrower given-away tokens `carried` and
  `ABSORB_UNITS` (both named verbatim by the procedure at lines 237 and 240) harvest 20/39
  each. One grep does not finish the answer — the log still supplies each entry's kind, stage
  and status — but it removes all 38 per-stage file visits, and the combination of that one
  grep with the log and the procedure page graded 12/12.
declaration: the figure each entry *applies* — `carried(stage)` for a `carry`,
  `ABSORB_UNITS(stage)` for a `relief` — is the decisive per-unit datum and is not declared.
  `harvest_units()` declares the post-entry *running figure* (`sc-101` → `2616`, `sc-139` →
  `3680`), which by construction never occurs under `seed/`; that is what made all four
  measures vacuous, and it is the same wrong-quantity error as `q08-main-luna`. Declaring the
  applied figure, one entry per datum with `path` pointing at the stage's page or module,
  would re-measure H1 at or near 1.000. `NOTES.md` §4 argues the inputs are "inputs only" and
  so out of scope for the measure; that is precisely the argument the round's standing
  property rejects.
shortcut: 2 files, score 12/12 — `docs/handbook/settlement-procedure.md` (the rules) and
  `data/settlement-log.csv` (the rows), plus two greps (`carried` over `docs/`, `ABSORB_UNITS`
  over `src/`) whose file paths supply the stage names. No per-stage file opened, and
  `config/manifest.json` not needed: the module's stage prefix is in the grep's own path. Run,
  not estimated — `SCORE 12/12`, `PASS`, `VERDICT correct`, rc 0. `NOTES.md` §9 self-reports
  four files at 12/12, which is already under the five-file floor; two is worse. The first of
  those two files is handed over in one hop, which `check_rung0.py` flags only as a note
  because it tests a threshold of two: `grep -rl carryover .` and `grep -rl chain .` each
  return exactly one file, `docs/handbook/settlement-procedure.md`, and both words are in
  `prompt.md`. That breaches the standing rule that no single word of the prompt may grep to
  exactly one load-bearing file.
notes_claims: every *number* verified against the tree — 290 lines, `## Replay rules` at line
  204, first `carried figure`/`ABSORB_UNITS`/`rebase` at 237/240/244, viewer 263 lines and
  9,872 chars with the opening entry at char 9,809, log 5,708 chars over 42 rows with `sc-101`
  at line 38 and char 4,905, sweep 24,715 of 33,384 = 74.0%, 42 paths and 6 hops. One prose
  claim fails: §2's "Entry *k* is found only by taking entry *k-1*'s identifier and searching
  for the row that seals against it." For every sealed row `previous` is exactly the entry id
  minus one, so `previous` is redundant with the identifier and the claim is false.
tiers: Haiku fails at the `rebase` rule — the opening entry's figure is the stage's basis,
  `carried` **plus** `ABSORB_UNITS` (procedure line 244, forty lines below the section
  heading, itself at line 204), and a model that stops at the first screen of the procedure or
  reads `rebase` as "set to the carried figure" is confidently wrong at all eight keys; a
  careful Sonnet-class model reads to line 246 and is not caught, so the two tiers do separate
  here. The 39 lookups and 39 additions are not the separator: the material is a CSV, a
  fixed-position table row and a fixed-position constant, so any model that writes a fifteen-
  line script does the whole replay in one shot, as I did.
tools: `tools/settlement_status.py` prints 9,872 bytes containing all 42 rows with entry,
  status, date, kind, stage, actor and seals-against, plus the resolved opening entry — the
  complete chain structure and every entry's kind and stage, i.e. everything the replay needs
  except the figures. `check_tools.py` scores it `units=0/39` only because the declaration is
  vacuous; on the honest datum it prints the ordering half of all 39 units. It is not by
  itself fatal — it reprints one seed file the solver reads anyway, and the procedure
  sanctions resolving the opening entry either way — but it is a finding.
shape: entry 20 (`sc-120`, `carry envelope`) is reachable without entries 1-19. Filtering
  `status == sealed` and sorting on the numeric part of `entry` reproduces the link-walked
  chain exactly — I tested equality against the walk and it holds for all 39 — so the
  `previous` column, declared in `LOAD_BEARING` as "the only artifact carrying the chain", is
  never consulted; the two void rows that seal mid-chain (`sc-140`→`sc-109`, `sc-141`→
  `sc-121`) are excluded by the status rule alone, and the void opener `sc-100` sorts first
  and is excluded the same way. Worse for the shape: `figure_final` does **not** need
  `figure_after_35`. Only one `rebase` exists and it is entry one, so every later entry is a
  commutative `+carried` or `-absorb`; I summed the 39 sealed contributions from a randomly
  **shuffled** list and got 3,680, the graded value, with no ordering and no intermediate
  state. Seven of the eight keys are prefix sums of a numerically sorted list and the eighth
  is order-free. The running balance is real serial arithmetic and section 4 does sanction a
  balance, but the selection half of the chain that `NOTES.md` §2 declares "twice over, by
  design" is decorative, and that plus the two-file shortcut is the same pair of defects that
  dropped `q08-main-luna`. Adjacent finding: the 19 `carried` figures are exactly 1200 + 40·i
  in `README.md`'s own stage-table order, so a solver who reads the README and two component
  pages can generate all nineteen from the pattern without visiting the other seventeen.
hard_to_do: yes — nothing is obfuscated, split across lines, encoded or hidden, and the split
  of a stage's two figures between its page and its module is a plainly stated rule rather
  than a trick, so the difficulty that remains is honest reading (the rules sit past line 200)
  and volume; but volume is what most of it is, and volume is scriptable.
fix: rewrite `data/settlement-log.csv` so the chain is not recoverable from the identifiers —
  give the sealed rows non-consecutive ids drawn from a shuffle (so `previous` is the only
  thing that orders them, and a numeric sort of the entry column produces a different and
  wrong order), and move one `rebase` entry into the middle of the chain (say at entry 22) so
  that the final figure is order-dependent and `figure_final` cannot be reached as an
  order-free sum. That single file change restores the selection half of the chain, makes
  every checkpoint depend on the walk rather than on a sort, and leaves the procedure, the
  grader and every mode-9 placement untouched. Re-declare `harvest_units()` on the applied
  figure at the same time and re-run `check_harvest.py`, which will then measure something.
