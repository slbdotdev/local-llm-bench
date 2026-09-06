# Glossary

*Every term this project uses in a sense a newcomer would not guess, alphabetically.*

This file exists because two reviews in a row turned on a phrase that two readers
understood differently, so most entries also say what the term is *not*. Where a term
here disagrees with a component document, the term here is the project's meaning and
the component document is loose prose.

## abandoned record

A record reaped after its stage's `window_s` elapsed without the record leaving the
`pending` state. Retained in the evidence store, never deleted, and never counted against a
ceiling: a ceiling counts what a stage is holding, and an abandoned record is by definition
no longer held.

*Not:* a record the stage refused because it was at its ceiling. That is a shed record, and
shed records are counted, in the shed count.

*See also:* evidence store, pending, shed count, `window_s`.

## accepted

A record a stage has taken responsibility for and has not yet finished with. The accepted
records are exactly the records that count against a ceiling; nothing else does. The word
carries the same meaning in the manifest, in every component document and in every module,
and it is the one term here that has never been in dispute.

*Not:* acknowledged. Nothing in this project acknowledges anything.

## advisory value

A number carried in a `config/manifest.json` section for a human reader. The assembler reads
a section only when that section is explicitly enabled and falls back to the module constant
otherwise, so a manifest number describes intent rather than behaviour, and it is never
authoritative over a module.

*Not:* a default. A default is what the code uses when nothing else is given; an advisory
value is not used at all in the ordinary case.

*See also:* manifest section, and PR-0148's *Why this is not a manifest question*.

## assembly

The run-time wiring of the stages the manifest names, in manifest order. Stages are not
imported at module scope, so the assembly order is the manifest order and nothing else: not
the order the modules happen to sort in on disk, not alphabetical, and not the order the
stages were migrated in.

*See also:* drain order, which is the reverse of this and of nothing else.

## audit period

The quarter a conformance report covers. It bounds which findings are *reported*; it does
not bound which material is *read*. An auditor reads the whole ledger every time, because a
migration completed three quarters ago still decides whether a divergence seen today is a
finding at all.

*Not:* the conformance window, which is a per-change grace period, is a different length,
and exists for a different reason.

## backfill

Re-running a stage over records it has already seen, to correct an earlier defect. A
backfill never changes a ceiling and never appears in the migration ledger. It is defined
here only because two readers in a row have gone looking for backfills in the ledger and
concluded from their absence that the ledger was incomplete.

## ceiling

The largest number of accepted records a stage will hold before it refuses new work. Every
stage has two of them and they are not always the same number. The two are the declared
ceiling and the effective ceiling, and the difference between them is the reason most of
this glossary exists.

*Not:* `limit`. That is a third number again, it is not a ceiling, and it agrees with itself
everywhere it is written. See legacy limit.

## component document

The page under `docs/` that describes one stage: its purpose, its owner, its configuration
table and a pointer to its history. A component document outranks a history entry and is
outranked by a policy record. It is what an operator reads, and its configuration table is
where the declared ceiling is written down.

*See also:* declared ceiling, policy record.

## conformance window

The period after a configuration change during which a divergence between a document and its
module is expected and is not reported. Ninety days from the change. It has expired for
every stage in this project and has not affected a report in over a year; it is kept here
because the phrase still appears in older records.

*Not:* `window_s`, which is a per-record timeout measured in seconds and has nothing to do
with conformance.

## counter-signature

The second name on a completed migration. In the ledger it is a `counter_signed` event whose
detail names the date of the `migrated` event it signs. A `migrated` event that no
`counter_signed` event names is an in-flight migration and is not complete; a `migrated`
event that a later `voided` event annuls did not happen, and no ruling reads it.

A stage therefore has exactly one date that a ruling reads: the `recorded_on` of its
counter-signed, un-annulled `migrated` event. `tools/ledger_dump.py` applies this rule and
prints the result on each stage's `-> migrated_on` line.

*Not:* the actor on the `proposed` event, who is usually, but not always, the same person as
the one who recorded the migration.

## declared ceiling

The ceiling a stage's component document states in its configuration table, in the `ceiling`
row. It is what an operator was told. It is emphatically not the `limit` row of the same
table, which is the pre-migration key the assembler still falls back to and which the
ceiling migration deliberately did not re-use.

*See also:* effective ceiling, legacy limit.

## drain order

Reverse manifest order. Never insertion order, never alphabetical, and never the order the
stages were migrated in.

## effective ceiling

The ceiling a stage actually enforces at run time: the module constant `ENFORCED_CEILING`,
in the stage's own module, and nowhere else. It is what the code does. It is written once
per module and is deliberately not carried in the manifest, in the operations table, in the
history or in the tests, because the migration ruled that a number with five copies has five
chances to be wrong — which is precisely what had already happened to the legacy limit.

*Not:* `DEFAULT_<STAGE>_LIMIT`, which sits a line or two away in the same module, still
agrees with all four of its other copies, and is a legacy limit.

## evidence store

Where a snapshot is written before a restart. A snapshot written after a restart is not
evidence and is not admissible in an incident review.

## in flight

A migration that has been recorded and not yet counter-signed. In-flight migrations are
visible in the ledger and are invisible to every ruling.

*See also:* counter-signature.

## in tolerance

A stage whose declared and effective ceilings differ by no more than the rounding the
migration tooling was permitted, which was zero. The phrase therefore means that the two
numbers are equal, and it survives only from the pre-migration tooling, which was permitted
a rounding of two.

*Not:* out of tolerance, which is retired and which was never this term's opposite.

## ledger event

One row of `data/migration-ledger.csv`. A stage has several: at least a `measured`, a
`proposed`, a `migrated` and a `counter_signed`, and a few stages also have an attempt that
was recorded and then annulled by a `voided` event. The ledger is an event log and not a
table of stages: there is no such thing as "the stage's ledger row", which is why amendment
A-3 could not be applied as written and was superseded.

*See also:* counter-signature, migration.

## legacy limit

The `limit` row of a component document, the `limit` field of a manifest section, the
`limit` column of the operations table, the `DEFAULT_<STAGE>_LIMIT` module constant, and the
number quoted in a stage's history entry. All five are the same pre-migration number and all
five still agree, because the ceiling migration did not touch any of them.

A legacy limit is not a ceiling and tells you nothing about conformance. The migration re-
derived every ceiling from observed load rather than carrying the old number forward, so a
stage's legacy limit and its ceilings are different numbers for every stage in the project,
and that difference means nothing at all.

*See also:* ceiling, observed load.

## manifest section

One entry in `config/manifest.json`, describing one stage. Carries advisory values. An
enabled section is read at assembly time; the rest describe intent and are read by people.

*See also:* advisory value.

## migration

The ceiling migration: the project-wide exercise that replaced the legacy limit with a
ceiling re-derived from observed load, stage by stage, over eighteen months. Every stage
completed it. The ledger records when each one did; the policy records decide what a date
means.

*See also:* counter-signature, ledger event, observed load.

## non-conforming record

A single record whose state is not one of the four its stage declares. This has nothing
whatever to do with a stage's conformance. The two phrases are unrelated, the collision is a
known nuisance, and it has already misled one review.

*Not:* a record held by a stage that is out of conformance. Those records are ordinary.

## observed load

The p99 count of accepted records over a sampling period. Every stage's ceiling was re-
derived from its observed load during the migration, and the sampling is recorded on the
stage's `measured` ledger event. Observed load is evidence for a ceiling and is never itself
a ceiling.

## out of conformance

A stage whose **declared ceiling** and **effective ceiling** are not the same number.
Nothing else makes a stage out of conformance.

A divergent `window_s` does not: see *out of tolerance*, retired. A manifest section that
disagrees with a module does not: see *advisory value*. A `ceiling` row that disagrees with
the same document's `limit` row does not, and never can, because those are two different
numbers by construction: see *legacy limit*.

Whether a stage that meets this description is *reported* is a separate question, and it is
settled by the policy records rather than here.

## out of tolerance

Retired. It meant a stage whose window differed from its documented window, and it was
retired when the migration separated ceilings from windows and windows stopped being a
conformance concern. It is not a synonym for out of conformance and never was one.

## pending

Accepted, not yet acted on. Counts against the ceiling.

## policy record

A numbered, dated ruling under `docs/policy-records/`. A policy record outranks a component
document; a component document outranks a history entry. A policy record is narrowed in its
own amendment log and nowhere else, and only the amendment marked in force applies.

*Not:* a history entry, however recent.

## sealed

A stage that will accept no further mutation. `seal()` is idempotent.

## shed count

How many records a stage refused in a window because it was at its effective ceiling.
Reported by the stage named in that stage's own history entry.

## snapshot

A sorted view of a stage's records. Insertion order is never part of any contract.

## spot check

A partial sweep of some of the stages. It is not a conformance report and is not accepted as
one; the phrase exists so that nobody files the one as the other.

## stage

One module under `src/`, one section of the manifest, one document under `docs/`, one dated
history entry, and several ledger events.

## superseded

A history entry, or an amendment, kept as evidence because later reasoning cites it. A
superseded item is never a live instruction, and a superseded amendment is never the one in
force.

## window_s

Seconds a record may stay `pending` before it is reaped. Documented per stage, and not a
conformance concern since the migration separated ceilings from windows.
