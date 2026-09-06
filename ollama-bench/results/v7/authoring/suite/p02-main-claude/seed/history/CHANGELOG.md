# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `attestation_store`: re-derived the bundle window to 15 s (history/0000).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-06-14

- `audit_flow`: narrowed the marker window to 30 s (history/0001).
- `docs/audit.md`: brought in line with the module constants.

## 2035-11-27

- `dispatch_gate`: widened the batch window to 180 s (history/0002).
- `docs/dispatch.md`: brought in line with the module constants.

## 2033-04-13

- `compaction_gate`: re-derived the bundle window to 15 s (history/0003).
- `docs/compaction.md`: brought in line with the module constants.

## 2034-09-26

- `backfill_store`: re-derived the window window to 180 s (history/0004).
- `docs/backfill.md`: brought in line with the module constants.

## 2035-02-12

- `reconcile_core`: widened the entry window to 45 s (history/0005).
- `docs/reconcile.md`: brought in line with the module constants.

## 2033-07-25

- `shard_flow`: re-derived the slot window to 45 s (history/0006).
- `docs/shard.md`: brought in line with the module constants.

## 2034-12-11

- `tenancy_view`: widened the marker window to 180 s (history/0007).
- `docs/tenancy.md`: brought in line with the module constants.

## 2035-05-24

- `cursor_gate`: widened the handle window to 60 s (history/0008).
- `docs/cursor.md`: brought in line with the module constants.

## 2033-10-10

- `throttle_view`: re-derived the marker window to 180 s (history/0009).
- `docs/throttle.md`: brought in line with the module constants.

## 2034-03-23

- `quota_flow`: narrowed the frame window to 30 s (history/0010).
- `docs/quota.md`: brought in line with the module constants.

## 2035-08-09

- `digest_flow`: narrowed the record window to 15 s (history/0011).
- `docs/digest.md`: brought in line with the module constants.

## 2033-01-22

- `rollup_flow`: re-derived the entry window to 120 s (history/0012).
- `docs/rollup.md`: brought in line with the module constants.

## 2034-06-08

- `watermark_view`: narrowed the marker window to 45 s (history/0013).
- `docs/watermark.md`: brought in line with the module constants.

## 2035-11-21

- `schema_flow`: re-derived the manifest window to 15 s (history/0014).
- `docs/schema.md`: brought in line with the module constants.

## 2033-04-07

- `ledger_flow`: widened the manifest window to 120 s (history/0015).
- `docs/ledger.md`: brought in line with the module constants.

## 2034-09-20

- `envelope_gate`: narrowed the batch window to 30 s (history/0016).
- `docs/envelope.md`: brought in line with the module constants.

## 2035-02-06

- `lineage_gate`: documented the marker window to 180 s (history/0017).
- `docs/lineage.md`: brought in line with the module constants.
