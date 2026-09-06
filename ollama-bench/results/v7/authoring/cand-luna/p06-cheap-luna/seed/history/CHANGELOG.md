# Changelog

Newest first. Every entry names the stage it touched and the history entry that
authorised it. An entry with no history reference was an emergency and is audited.

## 2033-01-01

- `shard_store`: widened the marker window to 60 s (history/0000).
- `docs/shard.md`: brought in line with the module constants.

## 2034-06-14

- `schema_core`: re-derived the token window to 120 s (history/0001).
- `docs/schema.md`: brought in line with the module constants.

## 2035-11-27

- `ingest_core`: re-derived the cursor window to 180 s (history/0002).
- `docs/ingest.md`: brought in line with the module constants.

## 2033-04-13

- `watermark_view`: re-derived the receipt window to 180 s (history/0003).
- `docs/watermark.md`: brought in line with the module constants.

## 2034-09-26

- `replay_view`: re-derived the entry window to 30 s (history/0004).
- `docs/replay.md`: brought in line with the module constants.

## 2035-02-12

- `routing_flow`: widened the slot window to 120 s (history/0005).
- `docs/routing.md`: brought in line with the module constants.

## 2033-07-25

- `envelope_flow`: documented the token window to 90 s (history/0006).
- `docs/envelope.md`: brought in line with the module constants.

## 2034-12-11

- `audit_core`: re-derived the cursor window to 45 s (history/0007).
- `docs/audit.md`: brought in line with the module constants.
