# Settlement procedure

*Kept by the settlement clerk. This page, with the amendment log at its end, is the procedure in force for the carryover settlement. A summary filed at a close is a snapshot of its own quarter: it records an outcome and never replaces, amends or interprets this page.*

## What the settlement is

At the close of every cycle the platform settles carryover: the balance of held-back
work that each stage brings out of the closing cycle and the platform takes into the
next one. The settlement reduces all of that to one number, the settlement figure,
denominated in the same units the assembler uses for its own limits. The figure is
quoted on the cycle's dashboards, in the quarterly review pack, and in any incident
review that touches capacity.

The settlement is not an adjustment of the stages themselves. No stage's own
configuration is read, written or rebalanced by a settlement. The figure is an
accounting of the platform as a whole, and it moves only through the settlement log.

A settlement is a replay, and the word is used deliberately. The clerk does not read the
figure off anything. The clerk rebuilds it, entry by entry, from the cycle's log, in the
order the log itself prescribes, and the figure at the end of the replay is the figure
the close reports.

## What the settlement is not

It is not the assembler's accounting. The `limit` and `window_s` figures on a stage's
page are the assembler's, they are echoed in five places each, and none of them is a
settlement figure. A settlement figure never appears in a manifest section, and a
manifest number is never a settlement figure.

It is not billing. Nothing in the settlement is denominated in money, and no settlement
paper is ever sent to Finance. The units are pipeline units and stay that way.

It is not retention. How long settlement paper is kept is the archive's business and is
governed by the retention policy, not by this page.

## Who runs it

One settlement clerk prepares the log, files each entry as the cycle produces it, and
closes the cycle. One reviewer countersigns. The clerk and the reviewer may not be the
same person, and an entry with a single signature is not a filed entry; it is a draft,
whatever it looks like.

Stage owners do not file settlement entries. A stage owner who believes the settlement
has mis-stated their stage writes to the clerk, who corrects by filing new entries and
never by editing filed ones. A filed entry is evidence.

The reviewer's countersignature means the replay was checked, not that the reviewer re-
derived it. Whoever re-derives the figure later does so from the log, and from nothing
else.

## Cadence and calendar

A cycle runs to the quarter. The log opens a few days before the cycle's first entry,
stays open while the cycle runs, and closes when the close summary is filed. Entries
carry the date they were sealed, which is the day the clerk signed them; a backfilled
entry carries its own signing date, which is why the dates in a log are not in any
useful order.

Between closes the figure does not drift. There is no standing adjustment, no accrual,
and no interest. The figure moves when and only when a filed entry moves it.

## Filing

The cycle's log is one file under `data/`, in the project's own comma-separated
convention, one row per entry as it was filed. The log is written by two clerks working
the same cycle at different times, which is why rows appear in the order they were filed
and in no other order.

The close summary for a finished cycle is filed under `docs/`, named for the quarter. A
summary states the figure the close reported and nothing else, because a summary that
carried the working would be quoted after the working had moved on.

This page, with the amendment log at its end, is the settlement procedure in force.
Where a summary, a slide or a review pack describes the settlement differently, the
discrepancy is reported to the clerk and this page is followed.

## Why the figure is replayed, never carried forward

Until 2035 the clerk carried the previous close's figure forward and applied the new
entries to it. That number had no provenance: when a quarter's dashboards disagreed with
the close by a wide margin, nobody could say which entry had been dropped, because the
starting number itself was the accumulation of every entry any clerk had ever dropped.

The rewrite settled it: the figure is rebuilt from the log every time it is needed. A
replay that disagrees with a filed summary is not a paradox to be reconciled; the
summary is stale and is corrected at the next close.

The same reasoning is why the log records what was done and the stages' own pages record
what the doing is worth. A log that carried the figures as well as the entries would go
stale against the stages the day either changed, and the project has been bitten by a
number with five copies once already.

## History of the procedure

The settlement began in 2033 as a paper form, one sheet per entry, filed in a binder by
the platform team. The binder is gone and the sheets were imaged during the 2035 move;
the images are retained as evidence and are not part of any replay.

The 2035 rewrite replaced the binder with the log file and the carried-forward figure
with the replay. It also introduced the counter-signature, after the spring cycle closed
twice with entries only one person had seen.

Two clerks have run the settlement since: the day clerk files as the cycle produces
work, and the late clerk clears the queue at the end of the week. Their filing
interleaves, which is why a log read top to bottom reads as noise.

The amendment log at the end of this page is complete. An amendment in force narrows the
procedure above; it never widens it, and a withdrawn or superseded amendment is never
applied.

## Common filing errors

A row filed twice after a clerk re-run. The second filing is withdrawn at the review and
stays in the log as filed, marked void. The log is never rewritten: the void marking is
the correction.

A row with the stage's name spelled loosely. Names are matched exactly as the manifest
spells them; a loose name is corrected by withdrawing the row and refiling it, not by
editing it in place.

A summary filed before the close finished. The close summary states the figure the close
reported; a summary filed early states a figure the close did not report, and the filing
checklist exists to catch it.

A draft that was never sealed. Drafts are removed from the binder at the review; in the
log they are marked void and kept, for the same reason the binder kept them: the log is
evidence of what was considered as well as what took effect.

## Signing and countersigning

The clerk signs an entry by filing it under their own name. The reviewer countersigns at
the review, and the review happens before the close, not after it. An entry that reached
the log without a review to countersign it is a defect in the filing, is reported, and
is voided at the next review.

The signatures are names in the log's own columns, not attachments. Nothing is attached
to a settlement entry, and a settlement entry never carries a figure in its own row: the
entry records the doing, and the stage's own material records what the doing is worth.

## What a replay is checked against

A replay run for a review is checked, not trusted. The checker walks the chain
independently and compares the figure at the end; a replay that disagrees with the
checker's walk is rerun from the opening entry, because a disagreement in the middle is
always an entry applied twice, applied from the wrong end, or not applied at all.

The checkpoints are what make a rerun bearable. A replay that states the figure only at
the end cannot be compared against anything but the end; a replay that states the figure
at each fifth entry can be compared entry band by entry band, and the first band that
disagrees is the band to rewalk.

Nothing else is compared. A replay is not checked against the dashboards, which lag the
close; not against the previous close, which answers a different question; and not
against any summary, which is a snapshot and not a walk.

## When the procedure is silent

A case this page does not cover is written up and put to the reviewer, and the pair of
them settle it before any entry is filed. What they settle is filed as an amendment at
the next revision of this page or as a note in the log itself; it is never settled by
analogy with a previous cycle's guess, and a guess filed as an entry is withdrawn at the
review like any other defect.

The reviewer keeps the list of settled cases with the page, and a case that recurs twice
is written into the next revision rather than left as a note. This page is shorter than
the list, and that is deliberate: a procedure that tried to enumerate every case a cycle
can produce would be wrong within the year.

## Terms

cycle - the quarter a settlement covers, from the first entry filed to the close.

close - the end of a cycle: the replay is run, the figure is reported, the summary is
filed.

figure - the settlement figure: one number, in pipeline units, rebuilt by replay from
the cycle's log. There is no other figure.

held-back balance - the units a stage brings out of a closing cycle and the settlement
admits into the figure.

take-back - the units a stage can absorb back out of the figure in the same cycle,
returning them to the stage's own working set.

entry - one row of the log: the record that something was done to a stage's balance at a
signing.

log - the cycle's file of entries as they were filed, in filing order and in no other
order.

summary - the close's one-page statement of the figure, filed under `docs/`. A snapshot
of its quarter, and never the procedure.

draft - an entry prepared and not sealed. Evidence of what was considered.

void - the marking the review puts on a row it withdraws. Kept as filed.

replay - rebuilding the figure from the log, entry by entry, in the order the log itself
prescribes.

opening entry - the entry the replay starts from. Defined by the replay rules below, and
resolved by the log viewer at the end of its output.

## Replay rules

*The rules of the replay. They are here, and not at the top, because the page is read by newcomers first for the institution and only later for the work; the work is below, and it is the work this page exists to state.*

### The log's columns

Each row carries: the entry's own identifier; the identifier of the entry it seals
against, empty for a row that seals against nothing; the date it was sealed; the clerk
who filed it; the kind of entry; the stage it was done to; the status, sealed or void;
and a note for the file. The columns mean what this page says they mean and nothing
else; the column names are the log's, not the settlement's.

### Which rows take effect

Only a row whose status is `sealed` takes effect. A `void` row is retained exactly as
filed, is never applied, and never extends the chain, whatever it seals against and
whatever date it carries. A void row is evidence that the entry was considered, and
nothing more.

### The chain is the order

The replay applies the sealed entries along the chain: the entry that seals against
nothing comes first, and each later entry is the sealed entry that seals against the one
before it. The chain ends at the entry nothing seals against. The filing order is never
the replay order, the dates are never the replay order, and no sort of either is a
replay. There is exactly one chain through a live log's sealed entries.

### Where an entry's figure comes from

An entry's row carries no figure, because a figure filed beside its entry goes stale
against the stage the day either changes. The figure an entry applies is read from the
stage's own material, by the kind of the entry:

a `carry` entry doubles the running figure, then adds the balance the stage's own
component page under `docs/` records and the running remainder for this stage; in
symbols, the new figure is `2F + balance + remainder`;

a `relief` entry triples the running figure, then subtracts the smaller of the stage's
take-back and the current figure; in symbols, the new figure is `3F - min(take-back,
F)`, and the remainder retained for this stage is the unapplied take-back, `max(take-
back - F, 0)`; the take-back is read from the stage's own module under `src/`, so the
amount applied is state-dependent;

a `rebase` entry does not adjust the figure but sets it: the figure becomes that stage's
settlement basis, its page balance plus its module take-back, read like a carry's and a
relief's;

The assembler's `limit` and `window_s` are settlement figures in neither role, and the
coincidence of a settlement figure with an assembler number means nothing.

### Where the replay starts

The replay starts at the chain's first entry: the sealed entry that seals against
nothing, whose `previous` column is empty. A void row that seals against nothing does
not start anything. The log viewer resolves the opening entry and prints it at the end
of its output; resolving it by hand from the log is the same work and is equally
sanctioned.

### Checkpoints

The figure after the kth applied entry, counting the chain's first applied entry as
entry one, is the kth checkpoint. The close reports the figure at the last entry of the
chain; the review sees the checkpoints, because a close that moved in one jump cannot be
audited.

## Amendment log

*Newest last. An amendment in force narrows the procedure above; it never widens it.*

### 2034-11-02 - clarified

The settlement figure is denominated in pipeline units. An earlier draft of the rewrite
had it in thousands; the dashboards never adopted that and the draft is withdrawn.

### 2035-08-19 - in force

The figure is replayed from the log and never carried forward. This is the rewrite
described in the history above, and it supersedes the carried-forward practice of every
earlier cycle.

### 2036-02-04 - in force

Void rows are retained as filed and are never applied, and the chain runs through sealed
entries only. Clarifies the 2035 rewrite; nothing else is narrowed.

### 2036-05-27 - in force

An entry's figure is read from the stage's own material by the kind of the entry. Before
this amendment the log carried each entry's figure beside it, which is precisely the
staleness the rewrite was about.
