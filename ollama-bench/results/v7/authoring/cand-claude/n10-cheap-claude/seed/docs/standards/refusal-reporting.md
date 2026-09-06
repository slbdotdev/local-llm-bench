# Refusal reporting standard

*How the quarterly refusal report is assembled, what it may say, and in what order it
says it.*

**This standard outranks `docs/architecture.md`, `docs/operations.md`, every component
page and every history entry.** Where one of those describes the report differently, it
is stale and is corrected against this page rather than the other way round.

## 1. Why the report exists

An operator who watches a record go into the pipeline and not come out the other end does
not conclude that a stage declined it on purpose. They conclude that something is broken,
and they escalate. Four of the six escalations in the last audit period were exactly that,
and three of the four consumed an on-call night to establish that nothing was broken at all.

The report exists so that a declined record is a written finding with an owner rather than a
silence. It is not a defect list, it is not a work queue, and it does not ask anyone to
change anything. It says what the pipeline declined, and it is read once a quarter by people
who were not on call when it happened.

Because it is read by people who were not there, its order matters more than its length. A
reader gets through the first few lines of a report and skims the rest, so the lines that
need acting on go first. Which lines those are is settled in section 4 and in the revision
log, and it has been settled differently at different times.

That last point is the reason this standard is as long as it is. Everything here except the
revision log has been stable for two years; the log is where the argument actually happened,
and it is at the end because that is where a log goes and not because it matters least. Two
of the three times this report has been re-derived by hand at a review, it was because
whoever assembled it had read the front of this page and stopped.

## 2. What a refusal is

A refusal is one record that one stage declined to admit. Each stage's own page under
`docs/` states, in one sentence, the single condition under which that stage declines a
record. The diagnostic code the refusal carries and the class of failure that code belongs
to are constants in that stage's own module, and are written nowhere else in the repository.

A refusal is therefore a pair: one record and one stage. A record that trips the conditions
of three stages produces three refusals, three findings and three lines in the report.
Nothing collapses them, and a report that collapses them has thrown away the only thing an
owner can act on, which is that it was *their* stage.

A refusal is not any of the following, and the report says nothing about any of them:

- an error. Declining is the stage working, not the stage failing.
- a retry. A declined record is not re-offered inside the quarter; the `hops` field counts
  what happened before the batch and never during it.
- a defect in the record. A record may be perfectly well formed and still be declined by a
  stage that is not prepared to hold it.
- a defect in the condition. The conditions are the stages' own and are correct by
  construction; a report is not the place to argue with one.

## 3. What is in scope

Every record in the quarter's batch as submitted, and every stage the pipeline assembles. A
sweep over some of the stages is a spot check, is not a report, and is not accepted as one;
the phrase is written down here so that nobody files the one as the other.

A record that no stage declines does not appear in the report. It is not written as a clean
line and it is not counted in a total: a report that lists what did not happen is a report
nobody finishes reading. The records that raised at least one finding are named separately,
because the first question the review asks is how many of the quarter's records were touched
at all.

The batch a report covers is the batch as submitted, in the order it was submitted, and
neither is negotiable. A record's position in that batch is not decoration: it is one of the
two things the reported order turns on, and a report assembled off a re-sorted copy of the
batch is a report assembled off different material. The batch file says so at the top of
itself, for the same reason.

## 4. The classes of failure

There are four. They are defined here in alphabetical order, which is the order a definition
list is written in and is not the order anything is reported in.

### admissibility

The record should not have been offered to the pipeline in this form at all. The finding is
against the submission and not against the record's contents: something about the shape of
what arrived means no stage downstream can reason about it.

*Not:* a record that is merely unusual. Admissibility is about the form of the submission,
and the form is a closed set with three members.

### custody

The chain of hands the record passed through cannot be established. Either too few counter-
signatures arrived with it, or it has been re-offered so many times that the chain has been
rewritten more often than it has been checked.

*Not:* a record whose signatures are present and wrong. That is a signing defect, it is an
incident rather than a finding, and it never reaches this report.

### saturation

The stage would have to hold more of the record than it is willing to hold. This is the only
class that is about the *stage's* capacity rather than about the record, which is why it is
acted on last: nothing about the record needs to change, and the conversation it starts is a
capacity conversation with a different team.

*Not:* the stage's `limit`, which counts records held at once and is a different number for
a different purpose. Saturation here is about one record at a time.

### staleness

The record is older than the stage is prepared to reason about. Two stages carry their own
view of how old is too old and the two numbers are not the same, on purpose: a stage that
keeps a record durable is prepared to accept an older one than a stage that is about to shut
down around it.

*Not:* `window_s`, which is how long a record may sit `pending` inside a stage once it has
been admitted. Staleness is measured on arrival and window is measured after.

### The order they are defined in

**The order in which the four classes are defined above is alphabetical and carries no
weight whatever.** The order in which findings are *reported* is a separate question, it has
been revised more than once, and it is settled in the revision log at the end of this
standard and nowhere else. It is deliberately not restated here: an order written down in
two places is an order with two meanings, and this project has already lost a quarter's
report to precisely that.

## 5. How a finding is written

A finding is written as the record's identifier, an oblique, and the diagnostic code:
`<record-id>/<diagnostic-code>`. Nothing else goes on the line. The findings are written as
one comma-separated sequence, in report order, and the sequence is the report; there are no
headings inside it and no blank lines between the classes.

The stage's name is deliberately absent. The code identifies the stage to anyone who needs
it and a name in a report reads as a person to blame, which is not what the report is for.
This was argued twice and settled the same way both times.

The records that raised at least one finding are written the same way, as a plain list of
record identifiers, and their order carries nothing: a record appears there once however
many findings it raised, and the list is a set rather than a sequence. It is written down
separately because the review counts it before it reads anything else, and counting it off
the findings means reading the findings first.

## 6. What the report may not carry

The report is quoted in review months after it is written, so it may carry only things that
will still be true then. It may not carry:

- the condition that was breached. Conditions change and a quoted condition goes stale; the
  stage's own page is the live copy.
- the numbers a record carried. Same reason, and worse, because a number in a report is read
  as a measurement of the stage rather than of the record.
- a count of anything. The review counts for itself off the sequence, and a count that
  disagrees with the sequence beside it has cost the report its credibility.
- a finding somebody has already dealt with. A report is a description of a quarter, not a
  list of open work, and a finding removed because it was closed is a quarter that reads as
  quieter than it was.
- a recommendation. The owners decide; the report describes.

The list is short on purpose and it is not a style guide. Everything on it was on a report
once, and every one of them cost an argument at a review that the report itself was supposed
to have prevented.

## 7. Who receives it, and when

It goes to the owner named on each stage's page, and to the platform review, within two
weeks of the quarter ending. Nothing is changed on the strength of the report itself: it is
a list of things that happened, and the owners decide which of them was supposed to.

The revision of this standard that the report was assembled under is cited on the report
itself, by identifier. That is not ceremony. The order has changed twice already and a
report whose order cannot be explained is a report that gets re-derived by hand at the
review, which has happened and took most of an afternoon.

A report is assembled under exactly one revision. Assembling half of it under one and half
under another is not a mistake anybody has made yet, but it is the mistake this section
exists to head off: the revision cited is the revision that produced every line of the
report, including the order of the lines, and a report that cites one revision and is
ordered by another is not evidence of anything.

## 8. Revision log

*Newest last. Only the revision marked **in force** applies. A superseded or a withdrawn
revision is kept because later reasoning cites it and because the argument is worth
having on the record; it is never a live instruction, and the most recent entry on this
page is not necessarily the one in force.*

### REV-1 - 2033-04-11 - superseded

Reported findings in the order the four classes are defined in section 4, which is
alphabetical, and within a class in the order the records were submitted. Superseded by
REV-3.

### REV-2 - 2033-09-02 - withdrawn

Proposed reporting by stage, in the order the pipeline assembles them, so that each owner's
findings arrived together. Withdrawn at review: a report grouped by stage is a work queue,
and the review reads the report to find out what happened to the quarter's records rather
than to hand out work. The grouping survives as the on-call triage order in
`docs/operations.md`, which is what it was always good for.

### REV-3 - 2034-01-24 - superseded

Kept section 4's alphabetical order and added the tie-break for a record that raises more
than one finding of the same class, which REV-1 had left undecided and which two people had
by then resolved two different ways. Superseded by REV-4, which changed the order of the
classes and kept this tie-break word for word.

### REV-4 - 2034-05-16 - **in force**

**Findings are reported by class, in this order of precedence: `admissibility` first, then
`custody`, then `staleness`, then `saturation`. Within a class, findings are ordered by the
position of the record in the batch as submitted. Where one record raises more than one
finding of the same class, those findings are ordered by the position of the raising stage
in `config/manifest.json`.**

The order between the classes is the order the findings have to be acted on, which is not
the order they sort in. A record that should never have been offered is withdrawn before
anybody asks who signed it, so admissibility goes first and custody second. Staleness is a
question about the record and is answered by the person who submitted it. Saturation is the
only one that is not about the record at all - it is a capacity conversation with a
different team, on a different timescale - so it goes last, and it goes last however many of
them there are.

The tie-break is REV-3's and is unchanged: manifest position, because that is the order the
record actually met the stages in, and a reader following one record down the sequence
should be following it forwards. It is emphatically not the stages' names in alphabetical
order, which is what the two people who disagreed in 2033 had each assumed the other meant.

This revision is the one in force. Cite it by its identifier on the report.

### REV-5 - 2034-07-08 - withdrawn

Proposed reporting in submission order throughout, class ignored, on the grounds that the
on-call runbook works a batch record by record and two orders for one thing is one order too
many. Withdrawn at review: a report in arrival order buries the admissibility findings among
the saturation ones, and the admissibility findings are what the report was created for.
REV-4 stands unchanged.
