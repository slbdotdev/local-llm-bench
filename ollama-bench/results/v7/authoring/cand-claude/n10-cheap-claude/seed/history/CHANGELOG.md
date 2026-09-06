# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `drain_core`: widened the marker window to 60 s (history/0000).
- `docs/drain.md`: brought in line with the module constants.

## 2034-06-14

- `quota_view`: widened the cursor window to 15 s (history/0001).
- `docs/quota.md`: brought in line with the module constants.

## 2035-11-27

- `ingest_view`: widened the record window to 120 s (history/0002).
- `docs/ingest.md`: brought in line with the module constants.

## 2033-04-13

- `backfill_flow`: re-derived the slot window to 90 s (history/0003).
- `docs/backfill.md`: brought in line with the module constants.

## 2034-09-26

- `attestation_core`: re-derived the record window to 120 s (history/0004).
- `docs/attestation.md`: brought in line with the module constants.

## 2035-02-12

- `checkpoint_gate`: re-derived the frame window to 120 s (history/0005).
- `docs/checkpoint.md`: brought in line with the module constants.
