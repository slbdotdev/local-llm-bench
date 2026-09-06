# The depth change journal, and how it is read

*Owner: the storage team. This document is the definition of the journal's meaning. The
filings themselves carry no rules, and the rules are written here and in no other file.*

## Why there is a journal and not a table

Retained depth used to be a number in a table, kept beside the array's capacity model and
edited whenever it changed. The table was wrong twice, both times because an edit was agreed
and never made, and the second time it was wrong for eleven weeks. The lesson the review drew
was not that the table needed an owner. It was that a current value with no history behind it
cannot be audited, and that a value which is only ever *derived* cannot silently disagree with
the record it is derived from.

So the record is the journal, and there is no table. The depth in force for a vault is a thing
you work out; it is not a thing you look up, and nothing in this repository will tell you what
it is.

## Where the journal lives

`ops/journal/` holds one file per change request, named for the request. A file is a
**filing**. The journal is every filing together and is never any one of them.

Lines beginning with `#` are filing notes and are not entries. The first line that is not a
filing note is the column header:

    seq  action  vault  size  target  filed_on  filed_by  reason

Fields are separated by tabs. A field that does not apply to an entry's action carries `-`.

## Which stage a vault belongs to

Each stage keeps its sealed segments in exactly one evidence vault, and the journal is filed
against vaults because the storage team owns vaults and the delivery teams own stages. The
vault a stage writes into is recorded in that stage's own document, in its *Retained depth*
section. It is recorded there and nowhere else: an index of vaults was kept for two quarters,
was wrong by the end of the first, and was withdrawn rather than repaired.

## The four actions

- **`apply`** names a vault in the `vault` column and, in the `size` column, the number of
  sealed segments that vault is to keep. That number is the vault's retained depth: the
  storage team's filings say `size` because a filing is about a store and not about a stage.
  The entry enters the journal **in force**.
- **`revert`** names an earlier `apply` entry by its `seq`, in the `target` column. If that
  entry is in force, it ceases to be in force. If it is not in force, the reversion is
  recorded and changes nothing.
- **`reinstate`** names an earlier `apply` entry. If that entry has been reverted, it is in
  force again. If it is already in force, the reinstatement is recorded and changes nothing.
- **`rescind`** names an earlier `apply` entry. The entry is **struck**: it ceases to be in
  force, and it can never be in force again, so a `reinstate` naming a struck entry is
  recorded for the audit trail and has no effect.

`revert`, `reinstate` and `rescind` name `apply` entries only. Naming anything else is a
filing error; there are none in the journal as it stands.

## The order entries are read in

Entries are read in ascending `seq`, across every filing at once. A `seq` is allocated when an
entry is filed and a filing may stay open for weeks, so a filing's entries are not contiguous
and two filings interleave. Reading one filing through and then the next gives a different
history from the one the journal records, and it is the most common way this journal has been
misread.

## The depth in force

At any point in the reading, a vault's retained depth is the depth of the highest-numbered
`apply` entry for that vault that is in force at that point. When no `apply` entry for a vault
is in force, the vault's retained depth is the depth its stage was commissioned with, which is
the `COMMISSIONED_DEPTH` constant in that stage's module.

A vault therefore returns to its commissioned depth whenever the last of its entries stops
being in force, and it does so without anything being filed to say so.

## When an entry changed something

An entry **changed something** when reading it changed the retained depth of a vault. An
`apply` naming the depth its vault already carries changed nothing; so did a `revert`, a
`reinstate` or a `rescind` that left every vault's depth where it was. Such entries are filed
and kept — a request that closes cleanly is worth the line it costs — and they are not
amendments to anything.

The distinction matters to the quarterly report, which cites the last entry that changed
something rather than the last entry filed. The two have not been the same number since the
programme's first quarter.

## What the journal does not carry

It does not carry a stage name, a commissioned depth or a current depth. It carries
amendments. Anything that looked like a current value in here would be a second source for a
number that already has one, and the review that created this journal was called after exactly
that.

## Filing discipline

1. An entry is never edited once it is filed. A mistake is corrected by a later entry that
   names it.
2. A striking is filed in the request that decided it, not in the request that carried the
   entry it strikes. That is what the `target` column is for.
3. A filing is closed when its request is closed, and no entry is added afterwards. Where a
   request was reopened, the filing notes say so.
4. The `reason` column is prose for a human reader and is never parsed. Nothing in this
   repository reads it, and nothing should.
