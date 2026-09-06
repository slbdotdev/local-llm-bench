# Incident 2034-09-04: the store and the dashboard do not agree

*Status: **open, inconclusive**. Raised by Platform Reliability. Not blocking the
quarter close.*

## What was seen

The reaper dashboard reports a hold for every stage. So does the evidence store, by
way of the filings in each stage's holdings file. For quarter 2034-Q3 the two do not
agree for any stage, and the dashboard is higher every time. On the dashboard's
figures all but one stage sits above the close-out ceiling, which is not what the
store's own files say.

## The dashboard's figures, as reported

The derived view, reproduced so the disagreement is on the record. These are not the
store's figures and are not authoritative: the close-out policy makes the store's own
files the record.

| stage | dashboard hold |
| --- | ---: |
| reconcile | 180 |
| backfill | 243 |
| dispatch | 139 |
| drain | 305 |
| checkpoint | 156 |
| rollup | 203 |

## What we could not establish

We spent two days on this and did not settle it. The open threads:

1. Whether the dashboard is counting something the store later took back, or the
   store is under-filing, or both. The two have different failure modes and we could
   not tell them apart from the dashboard's own logs.
2. Why the gap is a different size for every stage. If one mechanism explained it we
   would expect one shape.
3. Whether the same gap existed in the two previous quarters. The dashboard keeps no
   history, so answering this means reconstructing it from the store, per stage.
4. Whether the refactor proposed in the TODO in `src/` would remove the class of
   problem or move it. Nobody has costed that.
5. Who owns the dashboard. It is not in the manifest and no team has claimed it.

Any of these is a week's work and none is required for the close, which proceeds from
the store's own files as the policy says. This incident stays open behind it.
