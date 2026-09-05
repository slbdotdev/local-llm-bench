# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `tenancy_gate`: re-derived the cursor window to 180 s (history/0000).
- `docs/tenancy.md`: brought in line with the module constants.

## 2034-06-14

- `drain_flow`: narrowed the bundle window to 45 s (history/0001).
- `docs/drain.md`: brought in line with the module constants.

## 2035-11-27

- `reconcile_flow`: re-derived the bundle window to 60 s (history/0002).
- `docs/reconcile.md`: brought in line with the module constants.

## 2033-04-13

- `schema_gate`: narrowed the manifest window to 45 s (history/0003).
- `docs/schema.md`: brought in line with the module constants.

## 2034-09-26

- `quota_store`: narrowed the window window to 60 s (history/0004).
- `docs/quota.md`: brought in line with the module constants.

## 2035-02-12

- `audit_flow`: documented the segment window to 15 s (history/0005).
- `docs/audit.md`: brought in line with the module constants.

## 2033-07-25

- `routing_gate`: re-derived the cursor window to 60 s (history/0006).
- `docs/routing.md`: brought in line with the module constants.

## 2034-12-11

- `digest_gate`: re-derived the record window to 45 s (history/0007).
- `docs/digest.md`: brought in line with the module constants.

## 2035-05-24

- `rollup_core`: widened the window window to 60 s (history/0008).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-10-10

- `shard_store`: widened the entry window to 120 s (history/0009).
- `docs/shard.md`: brought in line with the module constants.

## 2034-03-23

- `attestation_store`: narrowed the manifest window to 90 s (history/0010).
- `docs/attestation.md`: brought in line with the module constants.

## 2035-08-09

- `dispatch_flow`: narrowed the frame window to 120 s (history/0011).
- `docs/dispatch.md`: brought in line with the module constants.

## 2033-01-22

- `compaction_view`: documented the segment window to 180 s (history/0012).
- `docs/compaction.md`: brought in line with the module constants.

## 2034-06-08

- `ingest_core`: widened the batch window to 60 s (history/0013).
- `docs/ingest.md`: brought in line with the module constants.

## 2035-11-21

- `envelope_flow`: narrowed the cursor window to 60 s (history/0014).
- `docs/envelope.md`: brought in line with the module constants.

## 2033-04-07

- `throttle_view`: widened the frame window to 180 s (history/0015).
- `docs/throttle.md`: brought in line with the module constants.

## 2034-09-20

- `lineage_flow`: documented the token window to 180 s (history/0016).
- `docs/lineage.md`: brought in line with the module constants.

## 2035-02-06

- `replay_core`: widened the frame window to 15 s (history/0017).
- `docs/replay.md`: brought in line with the module constants.

## 2033-07-19

- `retention_gate`: narrowed the cursor window to 90 s (history/0018).
- `docs/retention.md`: brought in line with the module constants.

## 2034-12-05

- `checkpoint_store`: re-derived the entry window to 60 s (history/0019).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-05-18

- `backfill_core`: narrowed the batch window to 90 s (history/0020).
- `docs/backfill.md`: brought in line with the module constants.

## 2035-01-12

- `settle_gate`: extracted the settle gate from throttle; the limit stays 24 (history/0021).
- `docs/settle.md`: new component document for the settle stage.
