# drain stage - evidence-store holdings, quarter 2034-Q3

*Store copy. Owner: N. Oyelaran (Compliance Review). Stage document: `docs/drain.md`.*

## What this file is

The evidence store keeps one holdings file per stage, and this is the drain one. Every
row in the register below is a filing: a batch of records placed into the store, or
released from it, with the date it happened and a note saying why. The stage's closing
hold for the quarter is the sum of the filings that still stand. Nothing in this file,
and nothing anywhere else in the repository, records that figure; it is worked out from
the rows.

A filing is written once and is never edited. A filing that turns out to be wrong is
taken back: a later line in this file withdraws it, and names it. The original row
stays where it is, because the store keeps what was filed as well as what stands.

## Register

| filing | date | records | note |
| --- | --- | ---: | --- |
| F-4351 | 2034-07-12 | +164 | placed from the backfill run of the same week |
| F-4355 | 2034-08-17 | +42 | carried in from the prior term at the close |
| F-4359 | 2034-08-22 | +134 | reaped after `window_s` and placed under the retention rule |
| F-4363 | 2034-09-03 | -35 | released to the long-term archive after review |

Withdrawn: F-4355 was withdrawn on 2034-09-18. The batch was counted twice by the
reaper and never reached the store, so this filing does not stand and does not count
toward the closing hold, in either direction.

## The filings in detail

**F-4351, 2034-07-12.** Placed from the backfill run of the same week. The run itself is in the changelog; what
is recorded here is only the batch that reached the store.

**F-4355, 2034-08-17.** The carry-over from the previous term. The store accepts one carry-over per stage per
quarter, and the records were already settled when they arrived.
This is the filing the withdrawal above names, and it does not stand.

**F-4359, 2034-08-22.** Reaped after the stage's own window and placed under the retention rule. Nothing in the
batch had settled, which is why it was reaped rather than released.

**F-4363, 2034-09-03.** Released to the long-term archive after review. An archived record is out of the store
and out of the hold, and the archive indexes what it took.

Not in this file: the stage's behaviour, which `docs/drain.md` describes, and the
retention term, which the policy pages set per record class.
