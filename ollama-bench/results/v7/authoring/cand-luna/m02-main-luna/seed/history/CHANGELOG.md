# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `quota_store`: documented the segment window to 90 s (history/0000).
- `docs/quota.md`: brought in line with the module constants.

## 2034-06-14

- `checkpoint_core`: re-derived the segment window to 60 s (history/0001).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-11-27

- `throttle_flow`: narrowed the segment window to 180 s (history/0002).
- `docs/throttle.md`: brought in line with the module constants.

## 2033-04-13

- `backfill_flow`: widened the segment window to 45 s (history/0003).
- `docs/backfill.md`: brought in line with the module constants.

## 2034-09-26

- `lineage_gate`: narrowed the receipt window to 90 s (history/0004).
- `docs/lineage.md`: brought in line with the module constants.

## 2035-02-12

- `retention_store`: documented the bundle window to 15 s (history/0005).
- `docs/retention.md`: brought in line with the module constants.

## 2033-07-25

- `watermark_gate`: narrowed the entry window to 45 s (history/0006).
- `docs/watermark.md`: brought in line with the module constants.

## 2034-12-11

- `routing_flow`: narrowed the frame window to 15 s (history/0007).
- `docs/routing.md`: brought in line with the module constants.

## 2035-05-24

- `rollup_gate`: widened the slot window to 60 s (history/0008).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-10-10

- `attestation_gate`: narrowed the marker window to 60 s (history/0009).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-03-23

- `dispatch_core`: narrowed the entry window to 180 s (history/0010).
- `docs/dispatch.md`: brought in line with the module constants.

## 2035-08-09

- `audit_gate`: documented the handle window to 30 s (history/0011).
- `docs/audit.md`: brought in line with the module constants.

## 2033-01-22

- `replay_flow`: re-derived the receipt window to 90 s (history/0012).
- `docs/replay.md`: brought in line with the module constants.

## 2034-06-08

- `ledger_gate`: re-derived the batch window to 120 s (history/0013).
- `docs/ledger.md`: brought in line with the module constants.

## 2035-11-21

- `compaction_gate`: narrowed the segment window to 120 s (history/0014).
- `docs/compaction.md`: brought in line with the module constants.

## 2033-04-07

- `cursor_view`: widened the token window to 45 s (history/0015).
- `docs/cursor.md`: brought in line with the module constants.

## 2034-09-20

- `envelope_core`: widened the receipt window to 45 s (history/0016).
- `docs/envelope.md`: brought in line with the module constants.

## 2035-02-06

- `digest_view`: narrowed the token window to 60 s (history/0017).
- `docs/digest.md`: brought in line with the module constants.

## 2033-07-19

- `tenancy_flow`: widened the segment window to 15 s (history/0018).
- `docs/tenancy.md`: brought in line with the module constants.

## 2034-12-05

- `ingest_core`: documented the marker window to 90 s (history/0019).
- `docs/ingest.md`: brought in line with the module constants.

## 2035-05-18

- `drain_view`: documented the manifest window to 120 s (history/0020).
- `docs/drain.md`: brought in line with the module constants.
