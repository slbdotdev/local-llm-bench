# 0004 - checkpoint: clarify the slot limit

- Date: 2034-05-18
- Status: **accepted**
- Proposer: M. Lindqvist (Compliance Review)

## Context

The checkpoint stage refuses work above `limit`, currently 250. Capacity Planning asked whether
that number is a safety limit or a cost limit, because the two imply different responses
to a refusal: a safety limit means shed load, a cost limit means queue and bill.

## Decision

It is a **safety limit**. The checkpoint stage sheds rather than queues, and `reconcile` is
responsible for reporting the shed count. The number itself is unchanged at 250.

## Consequences

- `docs/checkpoint.md` states the current behaviour and is authoritative over this entry.
- No change to `DEFAULT_CHECKPOINT_LIMIT`.
- The Compliance Review team owns the shed-count dashboard.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
