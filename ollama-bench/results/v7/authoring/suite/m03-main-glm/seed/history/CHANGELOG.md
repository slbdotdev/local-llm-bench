# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `reconcile_gate`: widened the token window to 120 s (history/0000).
- `docs/reconcile.md`: brought in line with the module constants.

## 2034-06-14

- `throttle_flow`: narrowed the token window to 30 s (history/0001).
- `docs/throttle.md`: brought in line with the module constants.

## 2035-11-27

- `backfill_gate`: widened the slot window to 30 s (history/0002).
- `docs/backfill.md`: brought in line with the module constants.

## 2033-04-13

- `attestation_view`: narrowed the receipt window to 60 s (history/0003).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-09-26

- `checkpoint_store`: documented the receipt window to 15 s (history/0004).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-02-12

- `compaction_store`: re-derived the marker window to 15 s (history/0005).
- `docs/compaction.md`: brought in line with the module constants.

## 2033-07-25

- `watermark_core`: re-derived the slot window to 15 s (history/0006).
- `docs/watermark.md`: brought in line with the module constants.

## 2034-12-11

- `ledger_flow`: widened the slot window to 45 s (history/0007).
- `docs/ledger.md`: brought in line with the module constants.

## 2035-05-24

- `dispatch_view`: widened the manifest window to 90 s (history/0008).
- `docs/dispatch.md`: brought in line with the module constants.

## 2033-10-10

- `replay_store`: documented the cursor window to 180 s (history/0009).
- `docs/replay.md`: brought in line with the module constants.

## 2034-03-23

- `envelope_store`: narrowed the record window to 180 s (history/0010).
- `docs/envelope.md`: brought in line with the module constants.

## 2035-08-09

- `audit_view`: narrowed the window window to 45 s (history/0011).
- `docs/audit.md`: brought in line with the module constants.

## 2033-01-22

- `routing_gate`: narrowed the receipt window to 60 s (history/0012).
- `docs/routing.md`: brought in line with the module constants.

## 2034-06-08

- `retention_core`: widened the entry window to 120 s (history/0013).
- `docs/retention.md`: brought in line with the module constants.

## 2035-11-21

- `digest_gate`: re-derived the record window to 30 s (history/0014).
- `docs/digest.md`: brought in line with the module constants.

## 2033-04-07

- `schema_flow`: widened the window window to 180 s (history/0015).
- `docs/schema.md`: brought in line with the module constants.

## 2034-09-20

- `rollup_gate`: narrowed the frame window to 120 s (history/0016).
- `docs/rollup.md`: brought in line with the module constants.

## 2035-02-06

- `quota_store`: re-derived the manifest window to 180 s (history/0017).
- `docs/quota.md`: brought in line with the module constants.

## 2033-07-19

- `lineage_flow`: documented the slot window to 15 s (history/0018).
- `docs/lineage.md`: brought in line with the module constants.

## 2034-12-05

- `shard_gate`: widened the record window to 60 s (history/0019).
- `docs/shard.md`: brought in line with the module constants.

## 2035-05-18

- `cursor_gate`: narrowed the bundle window to 90 s (history/0020).
- `docs/cursor.md`: brought in line with the module constants.

## 2034-10-28

- `docs/ops-calendar.md`: added the calendar page as the authoritative freeze schedule; the November train is cancelled and no November window is entered (history/0021).
