# NOTES — p01-main-glm (behaviour 1, rung 0)

## 1. Failure mode

Mode 1: a requirement stated once, far from the code. The promise that decides the answer
— a delivery a stage has acknowledged stays replayable for the whole of its
thirty-day replay term — occurs in exactly one sentence of one file, `docs/releases/rel-2032-11.md`
(the release 2.0 rationale, dated 2032-11-08, **in force**), at **line 19 of
41**; `facts()` fails the build if the phrase appears in any other seed file, so
"never repeated" is a measurement, not a wish. The tree's own neighbourhood — the
operations and README story of a nightly sweep that empties stores, and every module's
shelf line saying what was taken — describes a fire-and-forget pipeline and never
mentions the promise. It measures whether a model reconciles the whole tree or answers
from the files it happened to open.

Public shapes adapted as design only (plan 3.2): **LoCoDiff**'s reconstruct-state-from-
records shape (the per-component answer is replayed out of records and stated nowhere) and
**NoLiMa**'s bridge (prompt → README/changelog → release folder → the one rationale; no
file the prompt's vocabulary can reach names it).

## 2. Rung 0: why the material is necessary

The answer is an aggregate over **every** component of three facts that live in two
different artifact kinds per component:

- its acknowledged deliveries — a 6-row log, oldest signature last, appended to the
  component's own page under `docs/`;
- its sweep waterline and its last sweep run-date — the two dated lines of the shelf line
  in the component's own module under `src/`.

A component does not meet the promise exactly when its waterline has passed its newest
acknowledgement while that acknowledgement's term — fixed only by the promise — had not
run out, and its own shelf line dates the run inside that window. No file assembles the
answer: `check_rung0.py` part B confirms it, the manifest names components and limits
only, the rationale names no component, and each of the 18 components' facts is split
across its page and its module. The prompt names no load-bearing file; the only pointer
it gives is the manifest (declared `named_in_prompt`), which is the roster and not the
answer. The smallest assembly the answer needs is 38 files: the manifest, the
rationale, and every component's page and module.

The measured traversal — the manifest, the two pointers that make `docs/releases/`
findable, the rationale, and every component page and module — is **23202 of
30369 material tokens (76.4%)**. The index-leak trap is designed out: the
generator has never heard of waterlines, shelf lines or signature logs, each is written
once, in one artifact kind, and no index file lists any of them — asserted at build
time: every waterline and run-date occurs in exactly one seed file, every horizon string
in none, and each newest acknowledgement sits on the last row of its own page's log.

## 3. The harvest declaration, honestly

`harvest_units()` declares **54 entries — three per component** — because each
component carries three decisive data, and the round's brief says a unit with two
decisive data is two harvest-unit entries:

- unit `<name>`, value = its **protection horizon** (its newest acknowledgement plus the
  term), e.g. attestation → 2035-01-16, backfill → 2035-01-19, checkpoint → 2035-01-07. Derived: `facts()` fails the build if any horizon string
  occurs anywhere under `seed/`, so the full value is stated nowhere and no grep can
  harvest it;
- unit `<name> ack`, value = its **newest acknowledged date**, stated on the last row of
  its page's log (measured: each sits on that last row, which is what the answer reads);
- unit `<name> waterline`, value = its **shelf-line through-date**, stated in its module
  (measured: exactly one file each).

The first build declared only the horizon and left both stated facts undeclared — the
re-review called that correctly dishonest, and it was right twice over, because the fixed
`| delivery | acknowledged |` table header and the fixed `last sweep …, cleared through …`
comment made one grep (`-C2 acknowledged`, `-C2 cleared`) — and, with no vocabulary at
all, one shared frame, `sweep cleared through` — carry all eighteen of each record. Both
fixed shapes are gone and `facts()` asserts them absent. The log rows are now bare
`DLV-… <day>` pairs — no words at all on a page's value-bearing lines — under a heading
each page picks for itself, and each module's two dates sit on their own labelled lines
(`ran:` / `through:`) under a sentence in that component's own words — so no
value-bearing line anywhere carries a two-word run for the frame harvest to match; no
two components share a record template (asserted pairwise).

The harvest measures are **computed at build time with the check's own rules** — same
part splitting, same ±2/±5 windows, same frame rule — over all 54 declared units,
so this section measures rather than predicts: widest single giveaway token reaches
**0.111** of the units at ±2 and **0.111** at ±5; the roster regex reaches
**0.222**; the frame harvest reads 0 — no value-line frame is shared by any two of the 54 units Every unit's own file is
clean of giveaway tokens within five lines of a value line (asserted); the one remaining
coincidence is the generated history entries' own `Date:` lines sitting two lines under
their proposal titles, which the widest token reaches through the bare year alone. What
IS stated anywhere — raw log rows, shelf lines, the term, the record id — yields every
input and no answer: the horizons, the set, and which comparison to run exist in no file.

## 4. Distinguishing condition, and the wrong courses the material rules out

Exactly **6** components do not meet the promise: `backfill`, `digest`, `quota`, `rollup`, `schema`, `watermark`. The build asserts
the ruling against each component's own recorded run-date, so no record contradicts it:
every violating stage's sweep ran inside the term it broke (backfill ran 2034-12-31, 19 day(s) before its horizon 2035-01-19, digest ran 2035-01-03, 15 day(s) before its horizon 2035-01-18, quota ran 2034-12-29, 7 day(s) before its horizon 2035-01-05), every lawful
stage's run at or after its horizon, and every untouched stage's run before the oldest
row its log still holds.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| report every emptied store (12 of 18) | reads the README/operations sweep story and the shelf lines, never finds the promise, applies no term | the promise fixes the term; 6 components' waterlines passed their newest delivery's horizon, so their clearing was lawful |
| apply the fourteen-day replay term | greps for the term, finds both release notes, takes the older one | REL-2031-02 is marked **superseded by REL-2032-11**, and the rationale declares itself the promise's only statement; the set comes out smaller (the +15-day stages were lawful under the old term) and every horizon is fourteen days short |
| date the horizon from the oldest acknowledged delivery | takes the log's first row instead of its last | the prompt defines the evidence as the final acknowledged delivery's date; every horizon then predates its own waterline, so the set empties and every date moves |
| list evidence for the affected components only | skims the fourth key | the prompt says "for every component in scope, in that same alphabetical order" |
| never find the rationale; answer from the nearest page | reads one component's page and its module, generalises | membership is a per-component comparison; the lawful and violating stages are interleaved in the manifest, so no local reading predicts the set |

Each wrong course produces a complete, well-formed, confident answer, which is what
makes it a distinguishing condition rather than a format trap.

## 5. Positive or negative

**Positive** — the report names components and dates. Mode 1's shape is "the requirement
changes what is true of the components"; an empty answer set would let a solver that
never opens the tree pass by luck, so the negative quota is left to the modes whose
answer is "leave it alone" (AUTHORING-BRIEF section 8.4).

## 6. Why the grader is sound

Eight subchecks, each proving one thing: the deliverable exists; it decodes as UTF-8;
its shape is exactly the four keys in the prompt's order (the grader normalises
trailing newlines, CRLF, a BOM, a leading blank line and trailing spaces, none of which
the prompt specifies); then one group per key — the term compared `loose` (case- and
separator-insensitive, the n03 lesson, because it is quoted from prose), the component
set compared as an ordered list because the prompt fixes alphabetical order, the record
id exactly, and the horizons as an ordered list of dates because the prompt fixes that
order too. Plus the integrity/scope subcheck: every pre-existing file byte-identical to
the seed, nothing created but the report. A wrong-but-plausible answer differs in a
specific group and lands at 7/8 or lower as `confidently_wrong`; an untouched sandbox
is `visibly_failed` with no traceback; a correct report beside any seed edit or extra
file is `unsafe`. The grader never repairs, runs or writes anything, so grading twice
answers the same thing twice (`probe_idempotence.py`).

The order-sensitive comparisons are adjudicated explicitly: the prompt states both
orders in as many words ("alphabetical", "in that same alphabetical order"), so a
violated order is a wrong answer, not a formatting preference — and the probe set
includes exactly that case, which lands `confidently_wrong`.

## 7. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` — 42 paths across 8 distinct causal hops,
against the plan's minimum of six paths and three hops. The acceptance trial must touch
at least five of them.

- `config/manifest.json` — the list of components in scope; the prompt names the manifest, not the answer (*enumeration*)
- `README.md` — points at docs/releases/ and states the log and shelf-line conventions (*convention*)
- `history/CHANGELOG.md` — the release entries that make the rationale findable from the tree's own index (*pointer*)
- `docs/releases/rel-2032-11.md` — carries the promise - the term, the ruling clause, and the declaration that it is the promise's only statement (*ruling*)
- `docs/releases/rel-2031-02.md` — the fourteen-day decoy; its supersession marker is what rules the old term out for a solver that greps the term and finds both notes (*supersession*)
- `docs/releases/rel-2033-05.md` — the newest release note; a careful reader confirms it amends nothing (*amendment-check*)
- `docs/routing.md` — routing: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/routing_core.py` — routing: its shelf line - how far its store has been emptied (*waterline*)
- `docs/replay.md` — replay: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/replay_core.py` — replay: its shelf line - how far its store has been emptied (*waterline*)
- `docs/backfill.md` — backfill: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/backfill_store.py` — backfill: its shelf line - how far its store has been emptied (*waterline*)
- `docs/envelope.md` — envelope: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/envelope_gate.py` — envelope: its shelf line - how far its store has been emptied (*waterline*)
- `docs/ingest.md` — ingest: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/ingest_flow.py` — ingest: its shelf line - how far its store has been emptied (*waterline*)
- `docs/digest.md` — digest: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/digest_view.py` — digest: its shelf line - how far its store has been emptied (*waterline*)
- `docs/attestation.md` — attestation: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/attestation_flow.py` — attestation: its shelf line - how far its store has been emptied (*waterline*)
- `docs/tenancy.md` — tenancy: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/tenancy_gate.py` — tenancy: its shelf line - how far its store has been emptied (*waterline*)
- `docs/watermark.md` — watermark: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/watermark_view.py` — watermark: its shelf line - how far its store has been emptied (*waterline*)
- `docs/retention.md` — retention: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/retention_view.py` — retention: its shelf line - how far its store has been emptied (*waterline*)
- `docs/reconcile.md` — reconcile: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/reconcile_store.py` — reconcile: its shelf line - how far its store has been emptied (*waterline*)
- `docs/rollup.md` — rollup: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/rollup_core.py` — rollup: its shelf line - how far its store has been emptied (*waterline*)
- `docs/dispatch.md` — dispatch: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/dispatch_view.py` — dispatch: its shelf line - how far its store has been emptied (*waterline*)
- `docs/checkpoint.md` — checkpoint: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/checkpoint_view.py` — checkpoint: its shelf line - how far its store has been emptied (*waterline*)
- `docs/quota.md` — quota: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/quota_store.py` — quota: its shelf line - how far its store has been emptied (*waterline*)
- `docs/drain.md` — drain: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/drain_core.py` — drain: its shelf line - how far its store has been emptied (*waterline*)
- `docs/shard.md` — shard: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/shard_gate.py` — shard: its shelf line - how far its store has been emptied (*waterline*)
- `docs/schema.md` — schema: its signature log, oldest last - the dates the horizon is computed from (*ack-date*)
- `src/quay/schema_gate.py` — schema: its shelf line - how far its store has been emptied (*waterline*)

## 8. Budget

Not a mode-8 task. The reading is the traversal of section 2; the writing is four
lines. The reference answer is 384 characters.

## 9. Near-miss table

Generated by `selfcheck.py` from `probes.json`, written from this spec's own reference
and wrong-but-plausible answers. The five perturbations — no trailing newline, two
trailing newlines, CRLF, a leading blank line, trailing spaces — must leave the verdict
`correct`, and the key-order violation must not: the prompt fixes the order, so that
case is adjudicated as a legitimate failure (`confidently_wrong`), and it is.

## 10. Derivability

Every value the reference asserts is measured from `seed/` at build time by this spec:
the horizons by reading each page's log back and applying the term; the set by comparing
each horizon against the waterline and run-date read back from its module; the term and
the record id by locating the one file that carries them. Nothing is typed twice, and
`facts()` fails the build on any disagreement between the design and the disk — including
the fairness invariants: a violating stage's recorded run must sit inside the term it
broke, a lawful stage's at or after its horizon, an untouched stage's before its oldest
table row.

## 11. Departures from the research idea (section 5, p01)

- **Mechanism 2 for the horizons, mechanism 1 for the two stated records.** The sketch
  varies per-unit prose over eight components. Here the derived datum (the horizon) is
  computed and stated nowhere — the brief's strongest answer — and the two stated raw
  records (newest acknowledgement, waterline) are declared as their own harvest units and
  defended the prose way: bare log rows under per-component headings, and two bare
  labelled dates under a shelf-line sentence written in each component's own words. The
  first build's fixed table header and fixed sweep comment were harvested 18/18 by one
  frame; both are gone, asserted.
- **The glossary hop is gone.** The sketch bridges prompt → glossary → release note →
  code. Here the promise is written in the rationale's own plain words, and the bridge
  is the discovery chain every repository already has: README and changelog point at
  `docs/releases/`, the changelog's release entries carry the ids, and the folder holds
  a superseded note and a later silent one. Same number of hops (four), no extra
  artifact kind to maintain.
- **`regression_evidence` is defined** as the protection horizon of every component in
  scope; the research left the key's content open. Defining it per-component-for-all is
  what makes every component page genuinely required, which is where most of the sweep
  lives.
- **One generated-tree boilerplate reword.** The changelog's per-entry line "brought in
  line with the module constants" sat two lines under the changelog's own unrelated
  2034/2035 entry headings; with the giveaway token `module` in it, those headings were
  one grep from every horizon's bare year. It now reads "brought in line with the
  constants in code". No record, date or decision is touched.
- **No departure on `TARGET_TOKENS`:** it is 26000, the main band's table value. The
  overlay carries the material the rest of the way because it is fat by design — every
  page and module gains the per-component records the answer replays. Measured material:
  30369 tokens, inside 29,000-36,000. Generated corpus before the overlay:
  78 files / 124,366 characters.
