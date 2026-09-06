# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `reconcile_store`: re-derived the batch window to 60 s (history/0000).
- `docs/reconcile.md`: brought in line with the module constants.

## 2034-06-14

- `backfill_store`: re-derived the record window to 90 s (history/0001).
- `docs/backfill.md`: brought in line with the module constants.

## 2035-11-27

- `dispatch_core`: documented the token window to 45 s (history/0002).
- `docs/dispatch.md`: brought in line with the module constants.

## 2033-04-13

- `drain_flow`: narrowed the window window to 15 s (history/0003).
- `docs/drain.md`: brought in line with the module constants.

## 2034-09-26

- `checkpoint_flow`: documented the slot window to 15 s (history/0004).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-02-12

- `rollup_gate`: narrowed the segment window to 90 s (history/0005).
- `docs/rollup.md`: brought in line with the module constants.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
