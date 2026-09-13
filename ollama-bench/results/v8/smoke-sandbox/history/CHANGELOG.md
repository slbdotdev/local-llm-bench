# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `checkpoint_flow`: widened the segment window to 45 s (history/0000).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2034-06-14

- `ledger_gate`: re-derived the window window to 90 s (history/0001).
- `docs/ledger.md`: brought in line with the module constants.

## 2035-11-27

- `reconcile_core`: widened the frame window to 45 s (history/0002).
- `docs/reconcile.md`: brought in line with the module constants.

## 2033-04-13

- `backfill_gate`: re-derived the slot window to 15 s (history/0003).
- `docs/backfill.md`: brought in line with the module constants.

## 2034-09-26

- `audit_core`: re-derived the handle window to 120 s (history/0004).
- `docs/audit.md`: brought in line with the module constants.

## 2035-02-12

- `digest_core`: widened the entry window to 15 s (history/0005).
- `docs/digest.md`: brought in line with the module constants.

## 2033-07-25

- `compaction_core`: narrowed the cursor window to 120 s (history/0006).
- `docs/compaction.md`: brought in line with the module constants.

## 2034-12-11

- `schema_core`: re-derived the window window to 120 s (history/0007).
- `docs/schema.md`: brought in line with the module constants.

## 2035-05-24

- `attestation_store`: re-derived the marker window to 30 s (history/0008).
- `docs/attestation.md`: brought in line with the module constants.

## 2033-10-10

- `quota_view`: documented the window window to 180 s (history/0009).
- `docs/quota.md`: brought in line with the module constants.

## 2034-03-23

- `drain_store`: widened the frame window to 90 s (history/0010).
- `docs/drain.md`: brought in line with the module constants.

## 2035-08-09

- `ingest_flow`: documented the slot window to 45 s (history/0011).
- `docs/ingest.md`: brought in line with the module constants.

## 2033-01-22

- `watermark_flow`: documented the slot window to 30 s (history/0012).
- `docs/watermark.md`: brought in line with the module constants.

## 2034-06-08

- `envelope_flow`: re-derived the bundle window to 60 s (history/0013).
- `docs/envelope.md`: brought in line with the module constants.

## 2035-11-21

- `replay_gate`: narrowed the slot window to 90 s (history/0014).
- `docs/replay.md`: brought in line with the module constants.

## 2033-04-07

- `cursor_gate`: narrowed the marker window to 45 s (history/0015).
- `docs/cursor.md`: brought in line with the module constants.

## 2034-09-20

- `throttle_gate`: re-derived the batch window to 90 s (history/0016).
- `docs/throttle.md`: brought in line with the module constants.

## 2035-02-06

- `retention_core`: documented the bundle window to 120 s (history/0017).
- `docs/retention.md`: brought in line with the module constants.

## 2033-07-19

- `dispatch_store`: narrowed the marker window to 90 s (history/0018).
- `docs/dispatch.md`: brought in line with the module constants.

## 2034-12-05

- `shard_store`: re-derived the bundle window to 45 s (history/0019).
- `docs/shard.md`: brought in line with the module constants.

## 2035-05-18

- `routing_store`: narrowed the manifest window to 120 s (history/0020).
- `docs/routing.md`: brought in line with the module constants.
