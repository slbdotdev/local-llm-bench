# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `envelope_gate`: narrowed the window window to 60 s (history/0000).
- `docs/envelope.md`: brought in line with the module constants.

## 2034-06-14

- `checkpoint_gate`: documented the segment window to 120 s (history/0001).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2035-11-27

- `schema_view`: narrowed the frame window to 45 s (history/0002).
- `docs/schema.md`: brought in line with the module constants.

## 2033-04-13

- `retention_view`: re-derived the slot window to 120 s (history/0003).
- `docs/retention.md`: brought in line with the module constants.

## 2034-09-26

- `backfill_flow`: widened the bundle window to 90 s (history/0004).
- `docs/backfill.md`: brought in line with the module constants.

## 2035-02-12

- `throttle_core`: widened the cursor window to 90 s (history/0005).
- `docs/throttle.md`: brought in line with the module constants.

## 2033-07-25

- `dispatch_store`: re-derived the batch window to 180 s (history/0006).
- `docs/dispatch.md`: brought in line with the module constants.

## 2034-12-11

- `audit_view`: widened the bundle window to 120 s (history/0007).
- `docs/audit.md`: brought in line with the module constants.

## 2035-05-24

- `attestation_flow`: narrowed the entry window to 180 s (history/0008).
- `docs/attestation.md`: brought in line with the module constants.

## 2033-10-10

- `routing_flow`: documented the receipt window to 90 s (history/0009).
- `docs/routing.md`: brought in line with the module constants.

## 2034-03-23

- `replay_view`: widened the cursor window to 30 s (history/0010).
- `docs/replay.md`: brought in line with the module constants.

## 2035-08-09

- `cursor_store`: widened the entry window to 120 s (history/0011).
- `docs/cursor.md`: brought in line with the module constants.

## 2033-01-22

- `reconcile_flow`: narrowed the token window to 30 s (history/0012).
- `docs/reconcile.md`: brought in line with the module constants.

## 2034-06-08

- `compaction_core`: narrowed the manifest window to 90 s (history/0013).
- `docs/compaction.md`: brought in line with the module constants.

## 2035-11-21

- `tenancy_core`: narrowed the receipt window to 60 s (history/0014).
- `docs/tenancy.md`: brought in line with the module constants.

## 2033-04-07

- `drain_gate`: widened the batch window to 90 s (history/0015).
- `docs/drain.md`: brought in line with the module constants.

## 2034-09-20

- `lineage_view`: widened the marker window to 120 s (history/0016).
- `docs/lineage.md`: brought in line with the module constants.

## 2035-02-06

- `shard_store`: re-derived the slot window to 120 s (history/0017).
- `docs/shard.md`: brought in line with the module constants.

## 2033-07-19

- `quota_view`: narrowed the receipt window to 60 s (history/0018).
- `docs/quota.md`: brought in line with the module constants.

## Fixture rework

- Replaced the fixed regression fixture with one `tools/build_fixture.py` assembles from a
  caller-supplied review of the stage documents and each stage's own module.
  `tools/legacy_check.py` is removed.
- `tests/test_regression_checks.py` predates this change and is not part of the current
  checks; see `docs/workflows/release-checks.md`.
