# Engineering precedents: reading the recheck bulletin series

- Status: **in force**
- Maintained by: Capacity Planning
- Applies to: every stage named in `config/manifest.json`

This page is the project's record of how the bulletin series is read. It exists
because two quarters in a row turned on the same question, which of a stage's
bulletins is the live one, and it was answered two different ways by two teams
reading the same directory. The policies under `docs/policy/` govern records, their
keeping and the evidence they leave; this page governs the series and the intervals
it amends.
Neither page answers the other's questions, and where a handover note or a review
slide disagrees with this page, this page is what the report applies.

## What the series is

The series is the directory `docs/bulletins/`. One file is one bulletin. A
bulletin's file name begins with its serial, `MB-014` for example, and ends in a
slug that names nothing. The slug is decoration: two bulletins may share a slug,
and several here do.

The series is its directory. A file's place in the series is its serial, and the
serials sort the filenames into series order, which is the order a directory
listing shows and the order every reference in this page uses.

## What a bulletin may change

A bulletin amends exactly the stages named in its own amendment table, one row
per stage, and changes nothing else. A stage a bulletin mentions in its prose is
mentioned, not amended: the table is the whole of a bulletin's effect, and a
prose mention is a pointer for the reader rather than a change to the stage.

A bulletin changes one thing about a stage or confirms one thing about a stage.
It never does both, and it never touches a second setting on the way past.

## The three intervals a stage has

Every stage carries three intervals and they are not the same number.

The **shipped interval** is what the stage's module fixes: the constant named
`RECHECK_S` in the stage's own module, and nowhere else. It is what the stage ran
before the series ever reached it.

The **documented interval** is what the stage's component document states: the
`recheck_s` row of that document's configuration table. It is what an operator
was told most recently. A document is carried along when somebody remembers to
carry it, which is not always, and the gap between the documented interval and
the effective one is a finding for the report, not a fault in this page.

The **effective interval** is what the stage actually runs. Which number that is
is fixed under *Which bulletin governs* below, and nowhere else.

## Recording, and what a serial is not

Each bulletin carries one `Recorded:` date, which is the day the request was
recorded with the mailroom. The recorded date is the bulletin's date and the only
date it has.

In April 2034 the mailroom re-filed the series and issued fresh serials in
re-file order. The re-file was a physical tidy-up of a filing cabinet, and its
order was the order the folders came out of the cabinet; it was not a date order
and was never meant to be read as one. Serials have issued in filing order ever
since, and a serial therefore says where a bulletin stands in the series and
nothing else about it.

## Corrections and withdrawal

A bulletin is never edited after it is recorded. A correction is a later bulletin
that says so, and a withdrawal is a later bulletin that says that instead. In
both cases the original file stays in the directory exactly as recorded, because
the series is append-only: a series whose past can change is a series whose past
nobody can trust.

## Who may file

Any team may request a bulletin through the mailroom. Capacity Planning records
it, gives it the next serial, and files it. Requests are logged rather than
authored, which is why the bodies are short and the tables are exact, and no
bulletin carries a signature or an owner.

## Cadence

There is no schedule. Bulletins are recorded when a stage's queue behaviour
changes, and the series is read back as a whole only by the quarterly recheck
report. A quiet quarter is ordinary, and a busy one is what a re-file produces.

## What the series does not carry

The series carries recheck intervals and nothing else. A limit change is a
manifest change governed by `docs/policy/`, a window change belongs to the
component document and the module, and a bulletin that arrived carrying either
would be refused at filing and sent back to the requesting team.

## Filing mechanics

A request reaches the mailroom with a stage's name and either one number or a
request to confirm. The mailroom copies what it was given into the amendment
table exactly as it arrived, gives the bulletin the next serial, and files it.
Nobody edits a table after filing, for any reason; a filing mistake is corrected
the way everything else here is corrected, by a later bulletin.

## Reading the series back

Reading one stage's history out of the series means reading every bulletin whose
table names the stage, and there is no shortcut: the directory is the only index
the series has, the slugs carry no meaning, and no artifact gathers the tables
together. The quarterly report reads all of it, every time, because a bulletin
recorded three quarters ago still decides what a stage runs today.

## What the quarterly report owes the review

The quarterly recheck report names the stages that are out of sequence, names
the stages whose documented interval is not their effective one, and carries one
total. It does not quote the bulletins back, does not name bulletins by serial,
and proposes nothing; it is a reading of the series as it stands, and the series
stays as it is underneath it.

## Serials in references

Other pages may cite a bulletin by its serial, and a citation is a pointer and
nothing more: citing `MB-014` does not make the bulletin the live one for a
stage, and a page that cites a serial without this page's rule is citing an
address, not a ruling. The quarterly report cites no serials at all, and the
citations in incident reviews are read back through this page like everything
else that touches the series.

## Archiving

The directory only grows. A bulletin is never moved out of `docs/bulletins/`, is
never renamed, and is never renumbered, not even when its stage is retired: the
serials are the series' history, and a gap in the serials is a gap in the
record. Storage pressure is not a reason to shrink the series; the files are
small and the questions they settle are not.

## Renamed and retired stages

The series names stages as they were named at recording time. No stage has been
renamed while the series existed, and the rule is written here for the day one
is: a renamed stage's older bulletins keep the old name, the report reads both
names back to the same stage, and nothing is re-filed to match. A retired
stage's bulletins stay exactly where they are; the stage stops appearing in the
report, not in the record.

## Refusals at filing

The mailroom refuses a request, and files nothing, when the request carries a
setting the series does not hold, a table row with a stage's name missing, or a
number in a field that is not a number. A refused request is sent back with the
reason and is not logged in the series; the serial it would have taken goes to
the next bulletin that arrives.

## The mailroom log

Alongside the directory the mailroom keeps a logbook of what it did and when it
did it: recordings, re-filings, refusals. The logbook is not part of the tree
and the report does not read it; the series is complete without it, and where
the logbook and the series disagree about anything, the series is what stands,
because the series is what the teams were shown.

## The quarterly reading

Once a quarter the operations team reads every table in the directory and
sets it against every stage's module and document. The reading takes as
long as it takes, and it is done in full every time, because the one quarter it
is sampled is the quarter a stale interval becomes an incident. What the reading
produces is the report; what it does not produce is changes, which go back
through the mailroom like everything else.

## Between recordings

A request that has been made but not yet recorded changes nothing: it is not in
the series, no table names it, and no stage runs differently because somebody
asked for it. The mailroom's pending folder is not a preview of the series, and
a stage whose request is still waiting runs exactly what the last recording left
it with.

## Wording

This page's terms are written in lower case in ordinary prose and in bold where
they are defined. The quarterly report uses the terms the way this page defines
them, and so does every memo that quotes the report; a memo that invents its own
word for a thing this page has named is rewritten before it is circulated.

## Where questions go

Questions about the series go to Capacity Planning, and the answer is always the
same two pointers: this page and the directory. Nobody answers a series question
from memory, and an answer that cannot cite one of the two pointers is not an
answer the teams may act on.

## Paper copies

A printed or screenshotted bulletin is uncontrolled the moment it leaves the
room it was printed in. The directory is the only controlled copy of the
series, and a paper copy that disagrees with the directory is wrong by
definition; nobody sets the paper back into the record.

## Handover notes and other leads

A shift handover's notes, a review slide, or a margin scribble may name stages
and may guess at what the series did. None of it is evidence. The series is the
record, this page is how the record is read, and anything else in the tree that
speaks about the series speaks as a lead and is checked against the record
before it is repeated.

## Which bulletin governs

Where more than one bulletin's table names a stage, the bulletin with the later
recorded date governs the stage and the other is superseded for that stage. The
recorded dates are the only thing that settles it: the series does not cite itself,
a serial says nothing about age, and no bulletin names another.

A stage whose name appears in no bulletin's table runs its shipped interval, and for
such a stage the shipped interval is the effective one.

A stage's **effective recheck interval** is therefore the value its governing
bulletin sets for it. A bulletin that confirms a stage's interval does so in words
and sets no number; the stage's effective interval is then its shipped interval
exactly as if the series had never reached it, and the confirming bulletin still
governs the stage for everything else on this page.

The effective interval is what the stage runs and what the report sums. The shipped
interval and the documented interval are evidence about the stage, and neither is
what the stage runs.

## Out of sequence

A stage is **out of sequence** when the bulletin that governs it does not stand last
for that stage in series order; that is, when a bulletin that names the stage stands
after the governing one in the directory's order.

The report's out-of-sequence line lists exactly the stages that meet that
description and nothing else. A stage with one bulletin is never out of sequence,
and neither is a stage whose governing bulletin stands last. A stage may be reached
by the series and still be in order; the report's other lines carry whatever else is
worth saying about it.
