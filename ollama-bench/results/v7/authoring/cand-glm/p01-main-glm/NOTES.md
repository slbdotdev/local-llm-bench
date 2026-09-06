# NOTES — p01-main-glm (behaviour 1, rung 0)

## 1. Failure mode

Mode 1: a requirement stated once, far from the code. The promise that decides the answer
— a delivery a stage has acknowledged stays replayable for the whole of its
thirty-day replay term — occurs in exactly one sentence of one file, `docs/releases/rel-2032-11.md`
(the release 2.0 rationale, dated 2032-11-08, **in force**), at **line 19 of
41**; `facts()` fails the build if the phrase appears in any other seed file, so
"never repeated" is a measurement, not a wish. The tree's own neighbourhood — the
operations and README story of a nightly sweep that empties stores, and every module's
sweep block saying what was cleared — describes a fire-and-forget pipeline and never
mentions the promise. It measures whether a model reconciles the whole tree or answers
from the files it happened to open.

Public shapes adapted as design only (plan 3.2): **LoCoDiff**'s reconstruct-state-from-
records shape (the per-component answer is replayed out of records and stated nowhere) and
**NoLiMa**'s bridge (prompt → README/changelog → release folder → the one rationale; no
file the prompt's vocabulary can reach names it).

## 2. Rung 0: why the material is necessary

The answer is an aggregate over **every** component of two facts that live in two
different artifact kinds per component:

- its acknowledged deliveries — a 6-row table, newest first, appended to the
  component's own page under `docs/`;
- its sweep waterline — one line in the component's own module under `src/`, stating how
  far the nightly sweep has cleared its store.

A component does not meet the promise exactly when its waterline has passed its newest
acknowledgement while that acknowledgement's term — fixed only by the promise — had not
run out. No file assembles the answer: `check_rung0.py` part B confirms it, the manifest
names components and limits only, the rationale names no component, and each of the
18 components' facts is split across its page and its module. The prompt names no
load-bearing file; the only pointer it gives is the manifest (declared
`named_in_prompt`), which is the roster and not the answer.

The measured traversal — the manifest, the two pointers that make `docs/releases/`
findable, the rationale, and every component page and module — is **23224 of
30392 material tokens (76.4%)**. The index-leak trap is designed out: the
generator has never heard of waterlines or acknowledged-delivery tables, each is written
once, in one artifact kind, and no index file lists either, so `check_index_leak.py` is
told nothing because there is no `DECISIVE_CONSTANT` to leak — the decisive per-unit
datum is not a module constant at all, it is a date the reader computes.

## 3. The harvest declaration, honestly

`harvest_units()` declares **all 18 components**, one entry each: unit = the
component's name, path = its page under `docs/`, value = its **protection horizon** —
the date its newest acknowledged delivery stopped being protected, e.g. attestation → 2035-01-16, backfill → 2035-01-19, checkpoint → 2035-01-07.
That is the per-unit datum the answer uses, for both per-unit outputs: membership is
this date compared against the component's waterline, and `regression_evidence` IS
this date for every component in scope.

**Every declared value is derived.** `facts()` scans every file under `seed/` and fails
the build if any horizon string occurs anywhere: the value is computed by the reader
from the component's table plus the term, and no grep can harvest a string that is
nowhere. That is research section 2.2's mechanism — "grep returns raw transitions or
ledger rows, possibly all of them, but no final state" — applied to every unit, which
this round's brief calls the strongest answer and the one to reach for first. The check
should report all 18 units derived and H1 = H2 = H3 = 0.0.

What IS stated, and why it does not hand the answer over: the raw records (ack dates in
18 pages, waterlines in 18 modules), the term, and the record id. A grepper can
pull all of that onto one screen; it then holds every input and no answer — the horizon
per component, the set, and even which comparison to run exist in no file. The two
stated per-unit records are also single-source by construction: `facts()` asserts that
"cleared through" occurs in exactly the 18 modules and the ack-table heading in
exactly the 18 pages, and measures that each sweep-state comment sits at least
7 lines from any line naming its own stage. The superseded fourteen-day note is
the decoy for a solver that greps the term and finds two notes; the supersession marker
and the rationale's "only statement" declaration rule it out.

## 4. Distinguishing condition, and the wrong courses the material rules out

Exactly **6** components do not meet the promise: `backfill`, `digest`, `quota`, `rollup`, `schema`, `watermark`.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| report every cleared store (12 of 18) | reads the README/operations sweep story and the module blocks, never finds the promise, applies no term | the promise fixes the term; 6 components' waterlines passed their newest delivery's horizon, so their clearing was lawful |
| apply the fourteen-day replay term | greps for the term, finds both release notes, takes the older one | REL-2031-02 is marked **superseded by REL-2032-11**, and the rationale declares itself the promise's only statement; the set comes out smaller (the +15-day stages were lawful under the old term) and every horizon is fourteen days short |
| date the horizon from the oldest acknowledged delivery | reads each table bottom-up | the prompt defines the evidence as the newest acknowledged delivery's date; every horizon then predates its own waterline, so the set empties and every date moves |
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
- `README.md` — points at docs/releases/ and states the ack-table and waterline conventions (*convention*)
- `history/CHANGELOG.md` — the release entries that make the rationale findable from the tree's own index (*pointer*)
- `docs/releases/rel-2032-11.md` — carries the promise - the term, the ruling clause, and the declaration that it is the promise's only statement (*ruling*)
- `docs/releases/rel-2031-02.md` — the fourteen-day decoy; its supersession marker is what rules the old term out for a solver that greps the term and finds both notes (*supersession*)
- `docs/releases/rel-2033-05.md` — the newest release note; a careful reader confirms it amends nothing (*amendment-check*)
- `docs/routing.md` — routing: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/routing_core.py` — routing: its sweep state - how far its store has been cleared (*waterline*)
- `docs/replay.md` — replay: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/replay_core.py` — replay: its sweep state - how far its store has been cleared (*waterline*)
- `docs/backfill.md` — backfill: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/backfill_store.py` — backfill: its sweep state - how far its store has been cleared (*waterline*)
- `docs/envelope.md` — envelope: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/envelope_gate.py` — envelope: its sweep state - how far its store has been cleared (*waterline*)
- `docs/ingest.md` — ingest: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/ingest_flow.py` — ingest: its sweep state - how far its store has been cleared (*waterline*)
- `docs/digest.md` — digest: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/digest_view.py` — digest: its sweep state - how far its store has been cleared (*waterline*)
- `docs/attestation.md` — attestation: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/attestation_flow.py` — attestation: its sweep state - how far its store has been cleared (*waterline*)
- `docs/tenancy.md` — tenancy: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/tenancy_gate.py` — tenancy: its sweep state - how far its store has been cleared (*waterline*)
- `docs/watermark.md` — watermark: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/watermark_view.py` — watermark: its sweep state - how far its store has been cleared (*waterline*)
- `docs/retention.md` — retention: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/retention_view.py` — retention: its sweep state - how far its store has been cleared (*waterline*)
- `docs/reconcile.md` — reconcile: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/reconcile_store.py` — reconcile: its sweep state - how far its store has been cleared (*waterline*)
- `docs/rollup.md` — rollup: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/rollup_core.py` — rollup: its sweep state - how far its store has been cleared (*waterline*)
- `docs/dispatch.md` — dispatch: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/dispatch_view.py` — dispatch: its sweep state - how far its store has been cleared (*waterline*)
- `docs/checkpoint.md` — checkpoint: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/checkpoint_view.py` — checkpoint: its sweep state - how far its store has been cleared (*waterline*)
- `docs/quota.md` — quota: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/quota_store.py` — quota: its sweep state - how far its store has been cleared (*waterline*)
- `docs/drain.md` — drain: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/drain_core.py` — drain: its sweep state - how far its store has been cleared (*waterline*)
- `docs/shard.md` — shard: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/shard_gate.py` — shard: its sweep state - how far its store has been cleared (*waterline*)
- `docs/schema.md` — schema: its acknowledged deliveries, newest first - the dates the horizon is computed from (*ack-date*)
- `src/quay/schema_gate.py` — schema: its sweep state - how far its store has been cleared (*waterline*)

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
the horizons by reading each page's table back and applying the term; the set by
comparing each horizon against the waterline read back from its module; the term and
the record id by locating the one file that carries them. Nothing is typed twice, and
`facts()` fails the build on any disagreement between the design and the disk.

## 11. Departures from the research idea (section 5, p01)

- **Mechanism 2 instead of mechanism 1.** The research sketch varies per-unit prose
  ("kept after receipt", "survives the acknowledgement") over eight components. Any
  stated per-unit value sits somewhere in the seed, and its harvest exposure then
  depends on line placement and vocabulary discipline for the life of the candidate.
  This round's brief calls the derived mechanism the strongest and asks for it first,
  so the per-unit values are computed dates and the "different vocabulary" lives in the
  two raw record kinds (page tables, module sweep lines) instead.
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
- **No departure on `TARGET_TOKENS`:** it is 26000, the main band's table value. The
  overlay carries the material the rest of the way because it is fat by design — every
  page and module gains the per-component records the answer replays. Measured material:
  30392 tokens, inside 29,000-36,000. Generated corpus before the overlay:
  78 files / 124,366 characters.
