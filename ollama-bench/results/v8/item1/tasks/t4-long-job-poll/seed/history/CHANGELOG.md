# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `retention_gate`: widened the segment window to 30 s (history/0000).
- `docs/retention.md`: brought in line with the module constants.

## 2034-06-14

- `lineage_store`: documented the bundle window to 45 s (history/0001).
- `docs/lineage.md`: brought in line with the module constants.

## 2035-11-27

- `backfill_flow`: widened the batch window to 45 s (history/0002).
- `docs/backfill.md`: brought in line with the module constants.

## 2033-04-13

- `dispatch_store`: documented the receipt window to 45 s (history/0003).
- `docs/dispatch.md`: brought in line with the module constants.

## 2034-09-26

- `drain_store`: widened the bundle window to 120 s (history/0004).
- `docs/drain.md`: brought in line with the module constants.

## 2035-02-12

- `tenancy_core`: documented the batch window to 90 s (history/0005).
- `docs/tenancy.md`: brought in line with the module constants.

## 2033-07-25

- `shard_view`: re-derived the cursor window to 120 s (history/0006).
- `docs/shard.md`: brought in line with the module constants.

## 2034-12-11

- `digest_gate`: re-derived the frame window to 60 s (history/0007).
- `docs/digest.md`: brought in line with the module constants.

## 2035-05-24

- `cursor_gate`: documented the token window to 120 s (history/0008).
- `docs/cursor.md`: brought in line with the module constants.

## 2033-10-10

- `routing_flow`: narrowed the segment window to 90 s (history/0009).
- `docs/routing.md`: brought in line with the module constants.

## 2034-03-23

- `watermark_flow`: narrowed the marker window to 90 s (history/0010).
- `docs/watermark.md`: brought in line with the module constants.

## 2035-08-09

- `replay_core`: documented the slot window to 45 s (history/0011).
- `docs/replay.md`: brought in line with the module constants.

## 2033-01-22

- `throttle_gate`: widened the marker window to 45 s (history/0012).
- `docs/throttle.md`: brought in line with the module constants.

## 2034-06-08

- `reconcile_store`: widened the manifest window to 30 s (history/0013).
- `docs/reconcile.md`: brought in line with the module constants.

## 2035-11-21

- `envelope_core`: documented the batch window to 15 s (history/0014).
- `docs/envelope.md`: brought in line with the module constants.

## 2033-04-07

- `compaction_flow`: narrowed the handle window to 30 s (history/0015).
- `docs/compaction.md`: brought in line with the module constants.

## 2034-09-20

- `audit_core`: re-derived the record window to 30 s (history/0016).
- `docs/audit.md`: brought in line with the module constants.

## 2035-02-06

- `rollup_gate`: widened the manifest window to 120 s (history/0017).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-07-19

- `attestation_core`: documented the cursor window to 15 s (history/0018).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-12-05

- `ingest_core`: re-derived the record window to 30 s (history/0019).
- `docs/ingest.md`: brought in line with the module constants.

## 2035-05-18

- `schema_gate`: documented the entry window to 15 s (history/0020).
- `docs/schema.md`: brought in line with the module constants.
