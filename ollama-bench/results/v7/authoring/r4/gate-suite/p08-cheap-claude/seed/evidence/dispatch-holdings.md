# dispatch stage - evidence-store holdings, quarter 2034-Q3

*Store copy. Owner: R. Okonjo (Compliance Review). Stage document: `docs/dispatch.md`.*

## What this file is

The evidence store keeps one holdings file per stage, and this is the dispatch one. Every
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
| F-4334 | 2034-07-09 | +74 | placed by the drain, after the snapshot was written |
| F-4338 | 2034-08-14 | +69 | placed from the backfill run of the same week |
| F-4342 | 2034-08-19 | -25 | released to the requesting team with the owner's sign-off |
| F-4346 | 2034-09-24 | +21 | reaped after `window_s` and placed under the retention rule |

Withdrawn: F-4346 was withdrawn on 2034-09-16. The batch was counted twice by the
reaper and never reached the store, so this filing does not stand and does not count
toward the closing hold, in either direction.

## The filings in detail

**F-4334, 2034-07-09.** Placed by the drain, in the ordinary way, after the snapshot for the run had been
written. A snapshot taken afterwards would not have been evidence.

**F-4338, 2034-08-14.** Placed from the backfill run of the same week. The run itself is in the changelog; what
is recorded here is only the batch that reached the store.

**F-4342, 2034-08-19.** Released to the requesting team, with the owner's sign-off attached to the request, and
counted out of the hold on the day the records left.

**F-4346, 2034-09-24.** Reaped after the stage's own window and placed under the retention rule. Nothing in the
batch had settled, which is why it was reaped rather than released.
This is the filing the withdrawal above names, and it does not stand.

Not in this file: the stage's behaviour, which `docs/dispatch.md` describes, and the
retention term, which the policy pages set per record class.
