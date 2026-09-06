# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `routing_core`: documented the token window to 60 s (history/0000).
- `docs/routing.md`: brought in line with the module constants.

## 2034-06-14

- `replay_core`: widened the window window to 30 s (history/0001).
- `docs/replay.md`: brought in line with the module constants.

## 2035-11-27

- `backfill_store`: narrowed the slot window to 60 s (history/0002).
- `docs/backfill.md`: brought in line with the module constants.

## 2033-04-13

- `envelope_gate`: documented the cursor window to 120 s (history/0003).
- `docs/envelope.md`: brought in line with the module constants.

## 2034-09-26

- `ingest_flow`: widened the handle window to 15 s (history/0004).
- `docs/ingest.md`: brought in line with the module constants.

## 2035-02-12

- `digest_view`: documented the cursor window to 45 s (history/0005).
- `docs/digest.md`: brought in line with the module constants.

## 2033-07-25

- `attestation_flow`: narrowed the slot window to 30 s (history/0006).
- `docs/attestation.md`: brought in line with the module constants.

## 2034-12-11

- `tenancy_gate`: widened the segment window to 30 s (history/0007).
- `docs/tenancy.md`: brought in line with the module constants.

## 2035-05-24

- `watermark_view`: documented the window window to 120 s (history/0008).
- `docs/watermark.md`: brought in line with the module constants.

## 2033-10-10

- `retention_view`: widened the bundle window to 90 s (history/0009).
- `docs/retention.md`: brought in line with the module constants.

## 2034-03-23

- `reconcile_store`: narrowed the cursor window to 15 s (history/0010).
- `docs/reconcile.md`: brought in line with the module constants.

## 2035-08-09

- `rollup_core`: documented the frame window to 60 s (history/0011).
- `docs/rollup.md`: brought in line with the module constants.

## 2033-01-22

- `dispatch_view`: widened the record window to 180 s (history/0012).
- `docs/dispatch.md`: brought in line with the module constants.

## 2034-06-08

- `checkpoint_view`: widened the manifest window to 120 s (history/0013).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-11-21

- `quota_store`: re-derived the batch window to 120 s (history/0014).
- `docs/quota.md`: brought in line with the module constants.

## 2033-04-07

- `drain_core`: documented the record window to 120 s (history/0015).
- `docs/drain.md`: brought in line with the module constants.

## 2034-09-20

- `shard_gate`: re-derived the segment window to 30 s (history/0016).
- `docs/shard.md`: brought in line with the module constants.

## 2035-02-06

- `schema_gate`: documented the cursor window to 90 s (history/0017).
- `docs/schema.md`: brought in line with the module constants.

## Releases

- 2033-05-19 - REL-2033-05: release 2.2 notes (`docs/releases/rel-2033-05.md`).
- 2032-11-08 - REL-2032-11: release 2.0 rationale (`docs/releases/rel-2032-11.md`).
- 2031-02-17 - REL-2031-02: release 1.4 notes (`docs/releases/rel-2031-02.md`).
