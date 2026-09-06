# rollup stage - evidence-store holdings, quarter 2034-Q3

*Store copy. Owner: K. Sorensen (Delivery Engineering). Stage document: `docs/rollup.md`.*

## What this file is

The evidence store keeps one holdings file per stage, and this is the rollup one. Every
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
| F-4385 | 2034-07-18 | +104 | reaped after `window_s` and placed under the retention rule |
| F-4389 | 2034-08-23 | +98 | placed by the drain, after the snapshot was written |
| F-4393 | 2034-08-04 | -26 | released back to the producing team on request |
| F-4397 | 2034-09-09 | +27 | carried in from the prior term at the close |

Withdrawn: F-4397 was withdrawn on 2034-09-22. The batch was counted twice by the
reaper and never reached the store, so this filing does not stand and does not count
toward the closing hold, in either direction.

## The filings in detail

**F-4385, 2034-07-18.** Reaped after the stage's own window and placed under the retention rule. Nothing in the
batch had settled, which is why it was reaped rather than released.

**F-4389, 2034-08-23.** Placed by the drain, in the ordinary way, after the snapshot for the run had been
written. A snapshot taken afterwards would not have been evidence.

**F-4393, 2034-08-04.** Released back to the producing team on request, under the access rules. The request and
the redaction it needed are filed with the team, not here.

**F-4397, 2034-09-09.** The carry-over from the previous term. The store accepts one carry-over per stage per
quarter, and the records were already settled when they arrived.
This is the filing the withdrawal above names, and it does not stand.

Not in this file: the stage's behaviour, which `docs/rollup.md` describes, and the
retention term, which the policy pages set per record class.
