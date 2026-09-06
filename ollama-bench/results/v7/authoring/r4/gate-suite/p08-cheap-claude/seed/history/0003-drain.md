# 0003 - drain: raise the window limit

- Date: 2033-10-07
- Status: **accepted**
- Proposer: N. Oyelaran (Compliance Review)

## Context

The drain stage refuses work above `limit`, currently 64. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The drain stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 64.

## Consequences

- `docs/drain.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_DRAIN_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
