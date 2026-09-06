# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `backfill_gate`: re-derived the entry window to 180 s (history/0000).
- `docs/backfill.md`: brought in line with the module constants.

## 2034-06-14

- `envelope_gate`: re-derived the marker window to 15 s (history/0001).
- `docs/envelope.md`: brought in line with the module constants.

## 2035-11-27

- `compaction_flow`: re-derived the segment window to 30 s (history/0002).
- `docs/compaction.md`: brought in line with the module constants.

## 2033-04-13

- `attestation_view`: re-derived the handle window to 15 s (history/0003).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-09-26

- `audit_gate`: widened the manifest window to 45 s (history/0004).
- `docs/audit.md`: brought in line with the module constants.

## 2035-02-12

- `checkpoint_gate`: re-derived the segment window to 30 s (history/0005).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2033-07-25

- `drain_store`: widened the segment window to 120 s (history/0006).
- `docs/drain.md`: brought in line with the module constants.

## 2034-12-11

- `replay_gate`: narrowed the entry window to 90 s (history/0007).
- `docs/replay.md`: brought in line with the module constants.

## 2035-05-24

- `routing_view`: documented the window window to 90 s (history/0008).
- `docs/routing.md`: brought in line with the module constants.

## 2033-10-10

- `ingest_gate`: re-derived the marker window to 60 s (history/0009).
- `docs/ingest.md`: brought in line with the module constants.

## 2034-03-23

- `shard_store`: documented the bundle window to 45 s (history/0010).
- `docs/shard.md`: brought in line with the module constants.

## 2035-08-09

- `rollup_view`: re-derived the batch window to 30 s (history/0011).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-01-22

- `retention_view`: narrowed the window window to 90 s (history/0012).
- `docs/retention.md`: brought in line with the module constants.

## 2034-06-08

- `quota_gate`: documented the marker window to 60 s (history/0013).
- `docs/quota.md`: brought in line with the module constants.

## 2035-11-21

- `tenancy_core`: widened the cursor window to 60 s (history/0014).
- `docs/tenancy.md`: brought in line with the module constants.

## 2033-04-07

- `throttle_view`: widened the batch window to 15 s (history/0015).
- `docs/throttle.md`: brought in line with the module constants.
