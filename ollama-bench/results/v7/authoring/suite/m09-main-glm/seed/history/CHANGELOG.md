# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `drain_store`: widened the entry window to 30 s (history/0000).
- `docs/drain.md`: brought in line with the module constants.

## 2034-06-14

- `lineage_flow`: documented the manifest window to 120 s (history/0001).
- `docs/lineage.md`: brought in line with the module constants.

## 2035-11-27

- `rollup_flow`: re-derived the receipt window to 120 s (history/0002).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-04-13

- `quota_flow`: widened the frame window to 180 s (history/0003).
- `docs/quota.md`: brought in line with the module constants.

## 2034-09-26

- `compaction_core`: widened the token window to 180 s (history/0004).
- `docs/compaction.md`: brought in line with the module constants.

## 2035-02-12

- `checkpoint_view`: documented the marker window to 90 s (history/0005).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2033-07-25

- `reconcile_view`: documented the entry window to 180 s (history/0006).
- `docs/reconcile.md`: brought in line with the module constants.

## 2034-12-11

- `shard_flow`: widened the entry window to 45 s (history/0007).
- `docs/shard.md`: brought in line with the module constants.

## 2035-05-24

- `audit_view`: widened the record window to 90 s (history/0008).
- `docs/audit.md`: brought in line with the module constants.

## 2033-10-10

- `attestation_flow`: narrowed the frame window to 45 s (history/0009).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-03-23

- `watermark_flow`: documented the handle window to 120 s (history/0010).
- `docs/watermark.md`: brought in line with the module constants.

## 2035-08-09

- `backfill_flow`: widened the window window to 180 s (history/0011).
- `docs/backfill.md`: brought in line with the module constants.

## 2033-01-22

- `digest_store`: re-derived the segment window to 15 s (history/0012).
- `docs/digest.md`: brought in line with the module constants.

## 2034-06-08

- `schema_gate`: documented the slot window to 45 s (history/0013).
- `docs/schema.md`: brought in line with the module constants.

## 2035-11-21

- `replay_store`: documented the handle window to 60 s (history/0014).
- `docs/replay.md`: brought in line with the module constants.

## 2033-04-07

- `cursor_core`: re-derived the marker window to 15 s (history/0015).
- `docs/cursor.md`: brought in line with the module constants.

## 2034-09-20

- `tenancy_core`: narrowed the receipt window to 60 s (history/0016).
- `docs/tenancy.md`: brought in line with the module constants.

## 2035-02-06

- `throttle_store`: re-derived the entry window to 60 s (history/0017).
- `docs/throttle.md`: brought in line with the module constants.

## 2033-07-19

- `ledger_core`: documented the cursor window to 120 s (history/0018).
- `docs/ledger.md`: brought in line with the module constants.

## 2034-12-05

- `routing_gate`: re-derived the entry window to 90 s (history/0019).
- `docs/routing.md`: brought in line with the module constants.

## 2035-05-18

- `ingest_view`: documented the entry window to 30 s (history/0020).
- `docs/ingest.md`: brought in line with the module constants.

## 2034-06-04

- `tools/timeline_dump.py`: added the quarantine timeline printer (history/0021).
- `docs/replay-policy.md`: amendment log brought up to date for the timeline.
