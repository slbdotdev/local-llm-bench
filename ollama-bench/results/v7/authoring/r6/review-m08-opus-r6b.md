verdict: REVISE
fair: no — the scored `primary_module` path occurs in **no** seed file, while the only two documents that state watermark's module path both state a form the grader scores `confidently_wrong`.
solved_it: yes — my blind answer matched `ref/closeout.txt` on all three lines; I nearly went wrong on exactly the path form, because `docs/watermark.md:3` tells the reader the module is `src/watermark_gate.py`.
checker: sound — ran the reference and two near misses under `/mnt/c/Users/slb/scoop/apps/python/current/python.exe` with `test.py` outside the sandbox: reference `SCORE 7/7 / VERDICT correct`, the doc-stated path `6/7 / confidently_wrong`, `./`-prefixed paths `4/7`; `selfcheck.py` all 12 rows pass and integrity/idempotence are clean.
shortcut: 22 files, score 3/3 — incident + the 19 stage documents + the two tracking documents. Not under five, so not a rung-0 failure by that rule, but 17 of the 19 declared load-bearing modules are never opened (see finding 2).
harvest: 19/19 by `capacity_ack` — one `grep -rni capacity_ack seed/` prints 40 lines carrying every stage's declared *and* confirmed code; the answer is finishable with zero per-unit opens.
tools: clear — `check_tools.py` ran all 19 modules, 0 bytes and 0 scored values printed.
notes_claims: two fail — `NOTES.md:40` (per-file map sums to 29986, not 29987) and `NOTES.md:49-51` ("no single grep assembles it").
tiers: Haiku fails at the 19×19 `capacity_ack` reconciliation, or takes `throttle` from `docs/TODO-refactor.md:22` as the narrowed stage; a careful Sonnet clears that step but is caught by the `primary_module` path form, which is a defect rather than difficulty.
workhorse_failure: defect — the step that most plausibly fails a careful Sonnet-class model is writing `src/watermark_gate.py` for `primary_module`, and that is what the tree's own prose tells it to write.
hard_to_do: yes — moving the criterion from `limit` to `capacity_ack` genuinely closed the old manifest/operations index route, but the same revision introduced the docs-side shortcut in finding 2.
fix: in `README.md:19-37` and each `docs/<stage>.md:3`, name the module by bare filename (`watermark_gate.py`) instead of the invented root `src/watermark_gate.py`, and give the docs-side `capacity_ack` codes values that are not the stage's roster index.

---

## Findings, most severe first

### 1. The expected `primary_module` path is stated nowhere and contradicted twice — `confidently_wrong` (REVISE)

The prompt directs the solver to "determine, from the project's own written material". Measured over all 86 seed files:

- `src/cordage/watermark_gate.py` (the scored value) appears in **0** seed files.
- `src/watermark_gate.py` appears in **2**: `seed/README.md:26` (the stage roster) and `seed/docs/watermark.md:3` ("*Owner: D. Ferreira (Data Stewardship). Module: `src/watermark_gate.py`.*") — the narrowed stage's own component document.
- **0** non-module files mention `src/cordage` at all. The only written hint is `config/manifest.json:3` `"package": "cordage"`, which the solver must combine with `"module": "watermark_gate"` into a rooted path no document ever exhibits.

Graded on the Windows interpreter, that documented form scores `SCORE 6/7 / FAIL [the primary module: wrong value for primary_module] / VERDICT confidently_wrong` — the harshest non-`unsafe` verdict, for a model that did every hop of the reasoning correctly and then quoted the repository about its own layout. `NOTES.md:45-47` is aware of half of this ("the generator asserts that `src/cordage/watermark_gate.py` occurs in none of the stage documents"), but treats it purely as an anti-leak property; the cost is that the anti-leak measure leaves a *wrong* path standing in its place. This compounds with finding 2: a solver taking the docs-first route never opens a module, so `src/watermark_gate.py` is the only module path it has ever seen.

The fix must not put the exact path into the docs (that would leak the scored value and defeat `check_index_leak.py`). Removing the invented root is enough: name the module `watermark_gate.py` in the roster and in each stage doc's line 3, so nothing in the tree asserts a rooted path the grader rejects.

### 2. The docs side alone betrays the stage; 17 of 19 declared load-bearing modules are never needed (REVISE)

The `capacity_ack` code in each stage document is exactly that stage's 0-based index in the README/architecture roster — checkpoint `CA-00`, attestation `CA-01`, … retention `CA-18`. Watermark, at index 7, is documented as `CA-06`. So over the 19 documents alone, sorted: **`CA-07` never occurs and `CA-06` occurs twice**. One grep over `seed/docs/` identifies the anomalous stage with no module ever opened; the cursor/watermark tie is settled either by the positional rule or by opening those two modules.

Consequence for the coverage gate:

| | tokens | share of material |
|---|---:|---:|
| declared LOAD_BEARING (`NOTES.md:43-45`, 43 paths) | 20638 | 68.8% |
| the 19 stage modules within it | 12299 | — |
| 17 modules a docs-first solve never opens | 11003 | — |
| **what a docs-first solve actually needs** | **9635** | **32.1%** |

`NOTES.md:43-45` says the declaration "clears the 50% floor by construction"; the corpus a correct answer genuinely requires is 32.1%, below that floor. `check_load_bearing.py` certifies 68.8% because it reads the declaration, not the solve. Giving the documented codes values unrelated to roster position removes the gap-and-duplicate signal and makes the module sweep real.

### 3. One grep harvests both sides; the frames are byte-identical at fixed offsets

`grep -rni capacity_ack seed/` returns 40 lines — all 19 declared codes and all 19 confirmed codes — and the single disagreement is readable straight off that output. The frames are maximally regular: the value is on **line 17 of every stage document** and **line 14 of every module**, so `sed -n 17p seed/docs/*.md` and `sed -n 14p seed/src/cordage/*.py` both work as clean attacks. `diff seed/docs/cursor.md seed/docs/watermark.md` differs in 6 hunks only, all template substitutions.

### 4. `NOTES.md:40` — a number that does not check out

> "The whole-corpus meter is 29983 material tokens; the per-file rounded map sums to 29987."

`MANIFEST.json`'s `files` map has 86 entries summing to **29986**. Everything else in NOTES verifies exactly: 43 LOAD_BEARING paths, 7 distinct hops, 0 duplicates, 20638 tokens, 68.83% ≈ 68.8%, `material_chars` 139841 (measured 139841 chars / 139859 bytes), 86 seed files, all 86 `seed_hashes` matching the tree, and `ref/closeout.txt` equal to `CONFIG["expect"]`. The stale value is consistent with `seed/docs/watermark.md` having been edited in this revision without the sentence being recomputed.

### 5. `NOTES.md:49-51` — the single-grep claim is wrong

> "No single grep assembles it either: the incident names no stage, the two tracking documents share no vocabulary with each other or with the incident beyond ordinary words…"

The two tracking documents share the decisive vocabulary: both are **keyed by the stage name**. Once hop 1 is solved, `grep -rn watermark seed/ --include=*.md` returns both decisive rows in one command — `docs/pending-migrations.md:13` → `history/0003-digest.md` and `docs/compatibility-guards.md:13` → `tests/test_quota.py`, i.e. two of the three scored values verbatim. Separately, `check_rung0.py` flags this itself and asks a reviewer to try the one-hop shortcuts; confirmed: `grep -rl obliges seed/` returns exactly `docs/pending-migrations.md`, and `compatibility` / `passing` reach `docs/compatibility-guards.md`. The prompt uses "obliges", "follow-up migration", "compatibility", "keep passing" verbatim, so hops 2 and 3 *are* locatable by the prompt's own vocabulary — contrary to the main-band criterion. I do not weigh this as fatal, because both documents carry six rows and the decisive row selector still comes from hop 1.

### 6. Minor

- `docs/policy/` is cited three times as the authority that outranks everything (`README.md:11`, `README.md:46`, `docs/operations.md:44`) and **does not exist**. It changes no answer, but it invites a solver to hunt for a tier of rules that is not there.
- Generator artifacts a careful reader will trip over: `src/cordage/watermark_gate.py:50` writes the state `"expandd"`, `docs/cursor.md:35` has `narrowd`, and `settled` is duplicated in both `WATERMARK_STATES` (`watermark_gate.py:15`) and `docs/watermark.md:35-36`. The prompt's "do not re-diagnose the defect yourself" keeps these from becoming wrong answers, but they read as corpus noise rather than a real repository.

## What I checked

Read whole, once: `prompt.md`, `NOTES.md`, `MANIFEST.json`, `test.py`, `ref/closeout.txt`, `seed/README.md`, `seed/docs/{operations,architecture,pending-migrations,compatibility-guards,TODO-refactor,watermark,cursor}.md`, `seed/docs/incidents/2035-04-shed-count-drift.md`, `seed/config/manifest.json`, `seed/history/{CHANGELOG,0003-digest,0007-watermark}.md`, `seed/src/cordage/watermark_gate.py`, `seed/tests/test_quota.py`, plus the `capacity_ack` line of all 19 documents and all 19 modules. I did not open `reviews/`, `authoring/r5/reviews/`, any other candidate, or `suite/`; I ran no `git`.

Checkers, once each from `authoring/`, all passing: `selfcheck.py` (12/12 rows), `probe_candidate.py` (CLEAN), `probe_idempotence.py` (7/7 → 7/7 ok), `r5/check_rung0.py` (rung 0 clear), `r2/check_index_leak.py` (clean), `r2/check_load_bearing.py` (43 paths / 7 hops / 68.8%), `r5/check_tools.py --verbose` (tools clear). Grader verdicts from the Windows interpreter as above.

## What remains uncertain

- Whether finding 1 empirically fails a Sonnet-class model. A solver must open `src/cordage/watermark_gate.py` to read `CA-07`, so it holds the true path — unless it takes the finding-2 docs-only route, which never opens a module. I could not measure the split without running arms; the acceptance trials will show it directly in any `6/7 confidently_wrong` row whose `primary_module` reads `src/watermark_gate.py`.
- Whether the roster-index `capacity_ack` assignment is deliberate or an artifact of the generator numbering stages in order. Either way it is exploitable; I did not read the generator (`r2/common.py`, `specs/m08_main_claude.py`) because they sit outside the candidate directory.
- The `./`-prefixed answer scoring 4/7 is arguably harsh, but the prompt's template shows no anchor and no reasonable model prefixes `./`; I did not weigh it.
