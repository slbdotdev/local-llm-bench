# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `audit_view`: re-derived the batch window to 120 s (history/0000).
- `docs/audit.md`: brought in line with the module constants.

## 2034-06-14

- `schema_store`: documented the receipt window to 45 s (history/0001).
- `docs/schema.md`: brought in line with the module constants.

## 2035-11-27

- `ingest_view`: documented the frame window to 45 s (history/0002).
- `docs/ingest.md`: brought in line with the module constants.

## 2033-04-13

- `checkpoint_gate`: narrowed the bundle window to 45 s (history/0003).
- `docs/checkpoint.md`: brought in line with the module constants.

## 2034-09-26

- `rollup_store`: documented the marker window to 30 s (history/0004).
- `docs/rollup.md`: brought in line with the module constants.

## 2035-02-12

- `attestation_view`: narrowed the bundle window to 90 s (history/0005).
- `docs/attestation.md`: brought in line with the module constants.

## 2033-07-25

- `throttle_view`: widened the frame window to 60 s (history/0006).
- `docs/throttle.md`: brought in line with the module constants.

## 2034-12-11

- `reconcile_flow`: narrowed the window window to 30 s (history/0007).
- `docs/reconcile.md`: brought in line with the module constants.
