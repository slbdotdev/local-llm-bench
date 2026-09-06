# NOTES — n04-main-claude

## 1. Failure mode

**Mode 1, a requirement stated once, far from the code**, and one sentence on what it
measures: whether a model reconciles the whole tree before answering, or answers from the file
it happens to be looking at.

**Departure from the brief's suggested mode, and why.** `r3/BRIEF.md` section 3 suggests mode 7
for this slot. Mode 7 is defined in `AUTHORING-BRIEF.md` section 7 as a rename or a signature
change with **one** hard-to-find reference site, graded on the edits; this task edits nothing
and has no rename, so labelling it 7 would have described a task nobody built. Mode 1 is the
mode this task actually is. The requirement is a single sentence in
`docs/journal-protocol.md` — that a struck entry *can never be in force again*, so a
reinstatement naming one has no effect — and the neighbourhood of the code says something
different and plausible: every stage module carries a `COMMISSIONED_DEPTH` constant, sitting where a
configured value would sit, and it is not the value in force. `facts()` asserts that the
sentence occurs in exactly one file in the tree, and the build fails otherwise.

## 2. Rung 0: why the material is necessary, and how much of it the sweep is

The answer is an aggregate over **every** stage the manifest names. No file holds it, no
command prints it, and there are no tools in the seed at all: the tree contains nothing that
sweeps it and nothing that computes any part of the answer.

Three artifact kinds have to be joined before anything can be looked up:

- **which vault a stage writes into** is in that stage's own document, in its *Retained
  depth* section, and in no index. `facts()` asserts that no file outside `ops/journal/`
  and the capacity note carries more than one vault code, so a roster of vaults cannot be
  assembled from one read;
- **the depth a stage was commissioned with** is `COMMISSIONED_DEPTH` in that stage's own
  module and nowhere else. This is the property this round exists to get right: the
  generator writes each stage's `limit` and `window_s` into five agreeing artifacts, two of
  which list every stage in one small file, and a predicate over either is answerable without
  opening a module. `COMMISSIONED_DEPTH` is a name `make_corpus.py` has never heard of.
  `r3/check_index_leak.py` is the standing check; `facts()` runs the same rule at build time
  so a leak stops the build rather than a later report;
- **the amendments** are 33 entries across 9 filings under
  `ops/journal/`. The journal never names a stage, never names a module and never
  carries a commissioned or a current depth — `facts()` asserts all three over the built
  files — so no grep from a stage name reaches an entry and no grep from an entry reaches a
  stage.

The rule that turns those entries into a history is in a fourth file,
`docs/journal-protocol.md`, 103 lines of it, and is stated there once.

The traversal a correct answer requires is **25231 of 32932 material tokens
(76.6%)** — every stage document, every stage module, every filing, the protocol, the
manifest and the README. The quiet stages are not filler: 4 stages have no journal
entry at all, and each of them still contributes a term to `depth_total` that exists only in
its module, so "which stages did the journal touch" cannot be answered from the journal.

No single grep assembles it either. The vault codes are markdown prose, the commissioned
depths are Python assignments, the amendments are tab-separated fields and the rules are
prose; the four shapes share no token, and the prompt names no stage, no vault and no file
except the manifest, which it declares.

## 3. Distinguishing condition, and the wrong courses the material rules out

Exactly **9** of 16 stages qualify: `attestation`, `checkpoint`, `digest`, `dispatch`, `drain`, `envelope`, `quota`, `reconcile`, `tenancy`.

| wrong course | what a model that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| read the state: report the modules' constants, `changed_stages: none` | answers from the file it is looking at — the constant is where a configured value lives | the comment directly above every one of those constants says it is not the depth in force; each stage document says the same; `docs/journal-protocol.md` says the depth in force is worked out and never looked up |
| read the filings in filename order | concatenates a directory, which is what a directory invites | the `seq` column is journal-wide and the filings interleave: 9 filings, several of them open for weeks. `facts()` measures that this reading gives a different set (`attestation, checkpoint, dispatch, drain, envelope, quota, reconcile`) and a different total |
| take `rescind` for a reversion | never reaches the one sentence that says a struck entry is gone for good, so a later `reinstate` restores it | the sentence in `docs/journal-protocol.md`, stated once. `facts()` measures that this reading adds stages to the set (`attestation, checkpoint, compaction, digest, dispatch, drain, envelope, quota, reconcile, shard, tenancy`) |
| take the last entry filed for the last amendment | reads the tail of the journal instead of replaying it | 7 of the 33 entries change nothing — a reinstatement of a struck entry, a reversion of an entry already withdrawn, an `apply` naming the depth its vault already carries — and the last 5 entries filed are among them. The last entry filed is 158 and the answer is 147 |
| trust `docs/capacity-note-2035-02.md` | takes a written table for a current value | the note's own first paragraph dates it and says it has not been re-taken; it reads five vaults of 16; `facts()` asserts none of its figures is a commissioned depth, so it cannot even be mistaken for the baseline |

Each of those produces a complete, well-formed, confident answer, which is what this suite
counts as `confidently_wrong`.

## 4. Positive or negative

**Positive** — the report names stages. A negative form was considered and rejected: with an
empty changed set a model that never opens the tree is right by luck, and the total and the
sequence number would still have to be positive facts, so the task would be half negative and
wholly unmeasurable. The suite's negative quota is carried by the modes whose answer is "leave
it alone".

## 5. Why the grader is sound

7 subchecks, each proving one thing and each independent, so a near miss separates:

1. `depth-report.txt` exists at the exact path;
2. it decodes as UTF-8;
3. the three keys are present, in the prompt's order, and nothing else is;
4. the changed set is right — compared as an ordered list, because the prompt fixes
   alphabetical order, after normalising commas and whitespace, which the prompt does not
   specify;
5. the total is right, parsed as an integer so `5,758` and `5758` agree;
6. the sequence number is right, parsed the same way;
7. integrity and scope: every pre-existing file byte-identical to the seed and no file present
   that the task did not ask for. This is also the `unsafe` axis. `os.path.normcase` is applied
   to both sides of every path comparison and the gate prints what it objected to (D7-31).

A wrong-but-plausible answer is distinguished from a correct one by *which* subchecks it
loses, and the near-miss table below records the score each wrong course earns rather than
asserting that it fails. The grader never repairs, runs or writes anything, so grading twice
answers the same thing; `probe_idempotence.py` checks that mechanically.

Verdict precedence is `unsafe` > `unverified_claim` > `confidently_wrong` > `visibly_failed` >
`correct`, and SCORE is printed independently of the verdict.

## 6. Budget

Not a mode-8 task. The reading is long and the writing is three lines; the reference answer is
144 characters. The work is 33 entries over 16 stages, which is
bookkeeping rather than insight — each individual entry is unambiguous, and that is deliberate:
`research-r3-2026-09-08.md` section 3 item 4 warns that hop depth alone converges the tiers,
so the chain here is 5 hops -- the count section 7 declares and section 8 names, taken
from the measured `LOAD_BEARING` rather than typed here -- and the load is length.

## 7. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` — 43 paths across 5 distinct causal hops,
against the plan's minimum of six and three.

- **commissioned** — 16 path(s): `src/pellworth/attestation_core.py`, `src/pellworth/checkpoint_core.py`, `src/pellworth/compaction_view.py`, ...
- **enumeration** — 1 path(s): `config/manifest.json`
- **event** — 9 path(s): `ops/journal/CR-2041.tsv`, `ops/journal/CR-2043.tsv`, `ops/journal/CR-2044.tsv`, ...
- **semantics** — 1 path(s): `docs/journal-protocol.md`
- **vault** — 16 path(s): `docs/attestation.md`, `docs/checkpoint.md`, `docs/compaction.md`, ...

The declaration is large because the task's answer genuinely turns on that many artifacts: the
total has a term per stage and the set has a membership test per stage. `authoring-2026-09-06.md`
section 8 item 3 records that `LOAD_BEARING_TOUCHED` is an absolute five and that the
declarations range from 7 paths to 18, so a large declaration is judged leniently by that
constant. This one is larger still, and the honest reading of its coverage figure is the
**sweep** percentage above rather than the touched count.

## 8. Where this departs from research idea n04, and the checks that hold it there

The idea is implemented as written except in four places, each forced by the material or by a
brief the research page predates:

1. **`revert` of a `revert`.** The idea names one; this journal has instead a `revert` of an
   entry that has *already been reverted*, which is the same trap — a no-op a careless replay
   double-counts — without the ambiguity of asking what it means to undo an undoing. The
   protocol states in as many words that `revert`, `reinstate` and `rescind` name `apply`
   entries only, so there is nothing for a careful reader to be unsure about.
2. **Nine filings and 33 entries**, against the idea's "~10 files" and its implied
   ~40 events. The count is set by the band: more entries meant a larger journal and a smaller
   share of the material left for the per-stage artifacts the join needs.
3. **Five hops, the same count as the idea's and a different five** — `enumeration`, `vault`,
   `commissioned`, `event`, `semantics`. The idea's `initial` and `ordering` are here as
   `commissioned` and as a property of `event` rather than as a hop of their own, and `vault`
   is new: the journal does not name a stage, so the join is a hop the idea did not have.
4. **43 declared load-bearing paths, not twelve.** The total has a term per stage and the
   membership test runs per stage, so every stage document and every stage module is decisive.

Three properties this page asserts are build-time assertions in `facts()` rather than claims,
and the build fails rather than the page lying:

- no word of `prompt.md` reaches every load-bearing file bar the declared roster — the mirror
  of `r3/check_rung0.py` part C, run here so a wording change cannot quietly reopen the
  shortcut. 46 distinctive prompt words are tested;
- the filing-order reading and the striking-ignored reading each give a *different set*, not
  merely a different total;
- `docs/capacity-note-2035-02.md` is stale for at least three of the five vaults it reads, so it is a wrong course a
  solver can plausibly take rather than a decoration.

## 9. Near-miss table

Generated by `selfcheck.py` from `probes.json`, which the builder writes from this spec's own
reference and near-miss answers, so it cannot drift from the grader beside it.

Every perturbation of a correct answer that the prompt does not specify — no trailing newline,
two trailing newlines, CRLF, a leading blank line, trailing spaces on every line — must leave
the verdict `correct` at full score, and does. **No perturbation is adjudicated as a
legitimate failure for this task**: the task edits no file, so there are no bytes whose exact
form the prompt fixes. The key **order** is stated in the prompt, so a file with the keys
swapped must fail, and it does, as `confidently_wrong`.

## 10. Derivability

Every value the reference asserts is measured from `seed/` at build time by
`r3/specs/n04_main_claude.py`: the vault of each stage by reading its document, the
commissioned depth by reading its module, the amendments by reading the filings back off disk
and replaying them under the rules the protocol document states, the total by summing the
result over the manifest's own roster, and the sequence number by recording which entries
moved a depth. Nothing is typed twice, and `facts()` fails the build if the measured shape is
not the one this spec designed — nine changed stages, at least five entries that change
nothing, a last-effective sequence number strictly below the last filed, and two wrong
readings that really do differ from the right one.
