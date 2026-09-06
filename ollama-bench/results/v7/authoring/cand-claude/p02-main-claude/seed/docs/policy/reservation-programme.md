# Policy: slot reservations and the reallocation programme

*What a stage's reservation is, which adjustment entries have taken effect, and how
much a stage is allowed to hold.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component
document and every history entry.** Where a document disagrees with this policy the
document is stale, and it is corrected by its own owner and by nobody else.

## Terms

**opening grant** - the number of slots a stage was assembled against when the
programme opened on 2033-09-04. It is the `OPENING_GRANT`
constant in the stage's own module and it is written nowhere else.

**adjustment entry** - one row of the *Reservation adjustments* table in a stage's
component document. Every entry the programme ever recorded for a stage is in that
table, including the ones that never took effect. The table is a record and never a
running total.

**effective adjustment** - an adjustment entry that is in the `ratified` state **and**
whose `dated` column is on or before the programme's closing date, 2034-06-30.
An entry in the `proposed` state was never ratified. An entry in the `withdrawn`
state was taken back by the review that filed it. An entry ratified after the closing
date belongs to the successor programme, which has not opened, and has not taken
effect here.

**current reservation** - a stage's opening grant plus the change of every effective
adjustment in its table, and nothing else. No file carries it. It is recomputed from
the record whenever it is needed, which is the whole reason the programme records
entries rather than totals.

**standing allowance** - the largest current reservation a stage may hold. It is set
by the amendment in force below and by nothing else.

**over-reserved** - a stage whose current reservation is greater than the standing
allowance. A stage whose current reservation equals the allowance is within it.

## What the programme was for

Slot budgets were set once, per stage, when the pipeline was assembled, and then
moved by whatever review happened to be in the room. By 2033 four documents gave four
different figures for the same stage and the assembler used a fifth. The reallocation
programme replaced all of that with one rule: a stage has an opening grant, recorded
once, and every change to it is an entry in the stage's own component document.

The programme opened on 2033-09-04 and closed on 2034-06-30. It is
closed: the entries are the record of what happened, and a successor programme has
been proposed and has not opened.

## Why the grant has one copy

A stage's `limit` and its `window_s` are each written in five places, and that is the
whole finding of the 2033 review: the number the programme replaced had five copies,
in the assembler's own stage list, the operations table, the component document, the
module and the stage's own test, and most of them were wrong at the moment anybody
looked. A number with five copies has five chances to be wrong. The opening grant has
one copy, in the module, and the entries that change it have one copy each, in the
component document.

The same reasoning is why no document carries a stage's reservation as a figure. A
figure is a copy; the entries are the record.

## What a review does, and does not do

A review reads the record and reports what it finds. It does not repair what it
measures: a reviewer who corrects a component document has thrown away the evidence
that the document was wrong, and the finding with it. Only the stage's own owner may
close a finding, by filing an entry or by correcting their own document, and the
owners are named at the head of each component document.

This is the same rule as the retention policy's and it is here for the same reason:
two of the findings in the last review period were closed by the reviewer who
raised them before anybody else saw them, and the review had then measured nothing.

## What is not a finding

- A component document whose prose disagrees with its own entries. The entries are the
  record; the prose around them is a summary and is not maintained.
- A snapshot compiled for a review. A snapshot is a figure as at a date and goes stale
  the moment the next entry is ratified. It is evidence of what a review was told, and
  it is never the reservation.
- A stage whose opening grant is above the allowance. The grant is where the stage
  started, not where it is.
- Anything that is not one of the stages the assembler names. A finding against
  something that is not a stage has no owner to send it to.

## Reporting

A report names the stages, sums their reservations and cites the amendment whose
allowance it applied. It does not carry the divergence sizes and it does not carry the
entries: a report that carries numbers is quoted after the numbers have moved.

## Amendment log

*Newest last. Only the amendment marked in force applies; a superseded amendment is
evidence of what was once true and is never a live instruction.*

### RP-1 - 2033-09-04 - superseded

Opened the programme and set the standing allowance at 3600 slots, which was the
largest grant any stage then held. Superseded by RP-3 once the intake sampling was
in.

### RP-2 - 2033-12-05 - withdrawn

Would have made the assembler's own stage list authoritative for reservations.
Withdrawn within a week: the assembler reads a section of that list only when the
section is enabled, so a figure in it describes intent rather than behaviour.

### RP-3 - 2034-02-20 - superseded

Set the standing allowance at 4200 slots. Superseded by RP-4 on the closing review's
own figures; it is kept because two later reviews cite its reasoning.

### RP-4 - 2034-07-04 - **in force**

Sets the standing allowance at 5000 slots, on the capacity the closing wave actually
left in the pool. This amendment is the one in force. Cite it by name in any
report of what a stage is holding.

