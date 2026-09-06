# PR-0148 - ceilings, and which one is authoritative

- Status: **in force**
- Supersedes: PR-0092 (ceilings are a manifest concern)
- Applies to: every stage named in `config/manifest.json`

## The ruling

Where a stage is **out of conformance** — the glossary carries the project's
definition of that phrase and this record does not restate it, because a definition
with two copies is a definition with two meanings — the code is what happens and the
document is what an operator was told. The divergence is therefore a documentation
defect and is reported as one. The module is never edited to match the document, and
the document is never edited during an audit: an audit that repairs what it measures
has measured nothing.

This record rules on **authority and reporting**. It does not say which stages are
out of conformance, what makes them so, or which comparison is the right one; those
are matters of definition and they live in `docs/glossary.md`, which is where this
project puts every term it uses in a sense a newcomer would not guess.

## Why this is not a manifest question

PR-0092 made `config/manifest.json` authoritative and it did not survive contact with
the assembler, which reads a section only when the section is enabled and falls back
to the module constant otherwise. A manifest number is therefore an **advisory
value** — the glossary's term, and the glossary's definition — and the ranking of
sources this record enforces follows from that: the module, then the component
document, then the manifest. What that ranking means for any particular kind of
disagreement is a question about what the terms mean, and it is answered where the
terms are defined and not here.

## Reporting

A conformance report names the stages, sums their effective ceilings, and cites the
amendment it applied. It does not name the divergence sizes: a report that carries
the numbers gets quoted after the numbers have moved.

## What a divergence costs

An operator who reads a number in a component document and then watches the stage
refuse work at a different one does not conclude that the document is out of date.
They conclude that the stage is broken, and
they escalate. Two of the three escalations in the last audit period were this, and
both consumed an on-call night to establish that nothing was broken at all.

That is the whole cost of a divergence and it is why the report exists. It is not a
correctness problem: the code does what the code says.

## Who may close a finding

The stage's owner, by editing the component document, and nobody else. In particular
an auditor may not, and an auditor who does has destroyed the evidence that the
finding existed. This is the same rule as the retention policy's, for the same reason.

## What is not a finding

Which *kinds* of disagreement count is a question of what the term means, and the
glossary answers it. This section is about what a **report** may and may not carry,
which is this record's business:

- A history entry that quotes an old number. History is dated and is evidence; it is
  never a live instruction, and a superseded entry least of all. Do not open a finding
  against a stage because its history disagrees with it today.
- A test that asserts a module constant. The tests assert the code and are correct by
  construction; a test is never evidence of a defect in the thing it asserts.
- Anything found outside the manifest's stage list. A finding against something that
  is not a stage has no owner to send it to, and an unaddressed finding is noise.
- A finding an auditor has already repaired. See *Who may close a finding*.

## How the report is used

It goes to the stage owners named in the component documents, one line each, and to
the platform review. Nothing is changed on the strength of the report itself: it is a
list of documents that need an owner's attention, and the owners decide.

The sum of the effective ceilings is carried because the review's first question is
always how much capacity the divergent stages actually hold, and computing it from
the report is quicker than reopening every module.

## Frequency and scope

Every quarter, over every stage in the manifest. A partial sweep is not a conformance
report and is not accepted as one; the phrase for a partial sweep is a spot check and
it is written down as one so that nobody mistakes it for this.

## History

PR-0092 made the manifest authoritative and was written before the assembler's
fallback behaviour was understood. PR-0121 tried to make the document authoritative
and was withdrawn within a week, because it would have required editing modules to
match prose. This record is the third attempt and is the first that survived a
quarter.

## Amendment log

*Newest last. An amendment in force narrows the ruling above; it never widens it.*

### A-1 - 2033-02-14 - withdrawn

Proposed reporting a divergence of one as clerical and excluding it. Withdrawn: the
migration tooling was permitted zero rounding, so a divergence of one is a defect
like any other.

### A-2 - 2033-08-30 - superseded

Required a conformance report to name the divergence sizes. Superseded by A-3, on
the grounds in *Reporting* above.

### A-3 - 2034-01-19 - superseded

Excluded any stage whose migration ledger row carried a single signature. The ledger
was rebuilt as an event log a month later and the test stopped parsing: a stage has
several rows and no one of them is *the* row. Superseded by A-4, which tests a date
instead. What a counter-signature settles is which attempt completed, and that is a
definition and belongs in the glossary, where it now is.

### A-4 - 2034-05-02 - **in force**

**A stage is reported as out of conformance only when its migration ledger row is
dated on or after 2034-06-01.** A stage that diverged before that date diverged under the
old tooling, which was permitted to leave the document behind, and its divergence is
a known and accepted debt rather than a finding. The ledger row, and only the ledger
row, settles the date; a history entry's own date is the date of a decision and not
of a migration.

This amendment is the one in force. Cite it by its identifier in any report.
