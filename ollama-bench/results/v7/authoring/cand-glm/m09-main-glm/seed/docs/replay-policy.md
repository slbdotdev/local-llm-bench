# Replay quarantine policy

*How batches are quarantined, how a quarantine is lifted, and how the quarantine
timeline is read. Owner: R. Okonjo (Capacity Planning).*

This policy is the authority on every quarantine question: on what a quarantine
is, on which timeline entries count as lifts, and on how a batch's history is
read when it is ambiguous. `docs/replay.md` describes the replay stage's module
configuration and defers to this file on quarantine matters. A page under
`docs/policy/` would outrank this file; nothing else does, and a history entry
never does.

## 1. Scope

This policy covers the quarantine of replay batches in the cinder-crest pipeline:
when a batch is quarantined, what a quarantine forbids, how a quarantine is
lifted, and how the timeline of those events is read afterwards. It does not
cover retention (see `docs/policy/` when pages exist there, and the manifest
otherwise), and it does not cover the drain order (`docs/architecture.md`).

## 2. What quarantine is

A quarantine is a hold on a batch that the replay stage cannot yet release into
recovery. A quarantined batch is retained in full - quarantining is never a
deletion and never a redaction - but it is excluded from replay ordering until a
lift is recorded for it.

Quarantine is evidence-preserving by design. The batch that broke its lineage
chain is exactly the batch the next audit will want to read, so a quarantined
batch is stored with its receipts, its manifest section and the timeline entries
that led to the quarantine.

## 3. Roles

- **Reviewer** - a member of Capacity Planning who signs a lift. A lift without
  a reviewer sign-off in its detail is procedurally invalid but still appears in
  the timeline; the timeline records what happened, not what should have.
- **On-call** - an engineer currently holding the recovery pager. On-call may
  quarantine on their own judgement and may confirm an existing entry, and may
  never lift except with a reviewer's sign-off.
- **Auditor** - a member of Data Stewardship reading the timeline after the
  fact. Auditors file annotations; they never lift.

## 4. The timeline export

Every quarantine event is appended to the timeline export at
`data/quarantine-timeline.csv`. The export is written once per event and is
never rewritten, resorted or cleaned up afterwards; it is the evidence copy.
`tools/timeline_dump.py` prints the export in reading order. Nothing but the
export tool reads the CSV with any expectation about its formatting.

The export is the only copy of the timeline. The ticket system links to it
rather than duplicating it (history/0021), so a question about a quarantine is
always answered from the export, directly or through the printer.

## 5. Kinds of entry

Each timeline row carries exactly one `kind`, from this closed set:

- `quarantined`
- `requarantined`
- `lifted`
- `annotation`

The kinds are named here because the export's field reference (Appendix B)
needs the closed set. **The operative effect of each kind - what it does to a
batch's quarantine state, and how several entries for one batch combine - is
fixed by the amendment log at the end of this file, not by this section.** When
a reader needs to know what an entry did, the reader goes to the amendment log;
this section deliberately stops short of saying.

What can be said here without pre-empting the amendment log is the bookkeeping:
entries are appended in the order the events were recorded, the printer sorts
them by date, then batch, then kind, and a batch is identified by its `CC-`
identifier in every entry that concerns it.

## 6. Reading a batch's history

To read a batch's history, take every timeline entry for the batch and read
them in date order. The questions a reader normally asks are:

1. Is the batch under quarantine now?
2. If it was lifted, which entry lifted it?
3. If two entries look as if they both lifted it, which one governs?

Question 1 and question 2 are answered by walking the entries against the
amendment log. Question 3 is the one this policy exists for, and the rule that
answers it was amended twice and now lives only in the amendment log; a reader
who guesses at it from the shape of the entries will sometimes guess wrong, and
the audit that followed the spring incident is the standing proof (see the QA
note of 2034-04, which guesses).

The procedure for question 3, without the rule itself: identify every entry
that the amendment log counts as a lift, then apply the amendment that governs
duplicates. Both steps are mechanical once the amendment log has actually been
read; neither can be done from the entry shapes alone.

## 7. Recording discipline

An entry is appended when the event happens, not when the paperwork closes. A
lift whose reviewer sign-off arrives a week late still carries its original
date, because the timeline records events, and a lift is an event. A correction
is a new entry that cites the old one in its detail; an entry is never edited
in place.

Detail strings are free text but are written to be grepped: they name tickets
(`KS-`, `AUD-`, `AU-` prefixes), they name stages, and they avoid abbreviations
that will not still be obvious in five years.

## 8. Interaction with the drain

A quarantined batch is skipped by the drain the way a `pending` record is not:
the drain neither seals it nor passes it downstream. When the assembler meets a
quarantined batch it records the skip in its own log and continues, which is
why a quarantine never blocks a drain and why drain logs are not evidence about
quarantines - the timeline is.

If a batch is quarantined mid-drain, the drain finishes for the batches it has
already admitted and the quarantined batch waits for the next assembly. There
is no in-flight repair; `docs/operations.md` applies to quarantined batches
exactly as it does to every other kind of hold.

## 9. Evidence and snapshots

A quarantine that ends in evidence for an audit produces a snapshot at lift
time, taken before the batch re-enters replay ordering. The snapshot is
addressed by the lift entry's date. Where a snapshot and the timeline disagree
about a date, the timeline governs: snapshots are taken by tooling that has
twice been wrong about time zones, and the timeline is appended by hand.

## 10. Common misreadings, and what they are not

- A batch that appears several times in the timeline is not thereby a batch
  with several lifts. Appearances and lifts are different counts, and the
  amendment log is what turns one into the other.
- An entry dated after a lift does not necessarily concern the lift. Read the
  kind and the detail, not the date adjacency.
- A still-open quarantine (a quarantined batch with no later entry) is a
  normal state and not an incident; several are open at any time by design.
- The printer's sort order is a reading convenience and implies nothing about
  precedence. Precedence comes from the amendment log or not at all.

## Appendix A: quarantine reasons

Reasons are recorded in the detail string of the `quarantined` entry, from this
catalogue:

- `lineage chain broken at segment N` - the batch's lineage chain does not
  close. The most common reason and the least urgent; the chain is usually
  rebuilt from the evidence store within a week.
- `checksum mismatch on receipt manifest` - the receipts do not match their
  manifest. Urgent when repeated for one batch; a single mismatch is usually a
  writer crash.
- `duplicate key in manifest section` - the assembler refused the batch twice
  under one key. This is a clerical duplicate of a manifest key, has nothing to
  do with lift entries, and is resolved by re-keying the manifest section.
- `shed window exceeded twice` - the stage shed the batch twice inside its own
  window (`docs/operations.md`). Quarantine is protective while the cause is
  found.
- `post-lift check failed` - the batch was lifted and then failed the check it
  is re-run under after a lift. Leads to a `requarantined` entry, not to a new
  quarantine of a new batch.
- `reviewer request` - a reviewer asked for the hold. Rare, and always cites a
  ticket in the detail.

## Appendix B: field reference for the export

`data/quarantine-timeline.csv` carries five fields and a header row:

| field | meaning |
| --- | --- |
| `date` | ISO date the event was recorded, `YYYY-MM-DD`, UTC |
| `batch` | the batch identifier, `CC-` followed by four digits |
| `stage` | the pipeline stage that recorded the event |
| `kind` | one of the four kinds in section 5 |
| `detail` | free text, written to be grepped (section 7) |

The printer at `tools/timeline_dump.py` reads this file, sorts it by date then
batch then kind, and prints each entry on one line. It adds no entries, hides
none, and changes no dates: what the printer shows is what the export holds.

The export currently runs from January 2034. Earlier quarantines are in the
evidence store and are out of scope for this file; if a question reaches back
before January 2034, the answer is fetched from the store rather than inferred.

## Appendix C: glossary

Terms as they are used in detail strings and in this file:

- **receipt** - the per-batch record a stage writes when it admits work; a
  batch's receipts are the first thing a quarantine snapshot captures.
- **manifest section** - the stage's own section of `config/manifest.json`. A
  batch inherits the configuration of the stage that recorded it.
- **lineage chain** - the ordered list of segments a batch was built from. A
  chain that does not close is the usual reason for a quarantine.
- **sign-off** - a reviewer's recorded approval. A sign-off is recorded in the
  detail string of the entry it approves and nowhere else.
- **evidence store** - the durable store snapshots are written to before a
  restart or a lift; see `docs/operations.md` for the restart order.
- **clerical duplicate** - a second recording of an event that happened once.
  The term is defined in the amendment log for lift entries specifically;
  everywhere else it means what Appendix A uses it to mean.
- **open quarantine** - a quarantined or requarantined batch with no later
  entry. Open quarantines are counted at each audit and are not incidents.
- **governing lift** - the lift entry that answers "when did this batch become
  replayable". Which entry that is, when a batch has more than one, is settled
  by the amendment log and by nothing else in this file.

## Amendment log

Amendments are dated and append-only. The text of an amendment is operative
exactly as written; this log is the part of the file that outranks the sections
above where the two ever disagree.

### Amendment 2034-02-19: what counts as a lift

Only entries of kind `lifted` are lifts. An `annotation` never lifts a batch,
never re-opens one, and never re-dates an existing lift; a batch that shows a
`quarantined` entry, one `lifted` entry and any number of `annotation` entries
has been lifted exactly once. A `requarantined` entry is not a lift either; it
puts a batch back under quarantine, and the batch it concerns is under
quarantine again from that entry's date until a later entry lifts it.

### Amendment 2034-04-14: duplicate lifts

A batch that carries more than one `lifted` entry carries a clerical duplicate.
The **earliest** `lifted` entry for the batch is the governing lift, provided it
falls after the batch's most recent `quarantined` or `requarantined` entry;
every later `lifted` entry for that batch is void and is read as a clerical
re-recording, not as a second release. When a question turns on when a batch
became replayable, the governing lift's date is the answer, and no later entry
moves it.

### Amendment 2034-05-30: print order is not precedence

Confirmed, after a question from a new starter: the printer's sort order was
chosen for scanning and carries no precedence. The amendments above are the
only precedence rules in this file, and neither the sort order nor the appendix
ordering changes them.
