# 0021 - replay: export the quarantine timeline

- Date: 2034-06-04
- Status: **accepted**
- Proposer: R. Okonjo (Capacity Planning)

## Context

Quarantine questions were answered by asking whoever remembered the incident.
The spring audit needed three answers that no one could give from memory, and
the desk note that tried (docs/quarantine-qa-note.md) got its batch wrong.

## Decision

The quarantine timeline is exported to `data/quarantine-timeline.csv`, one row
per event, and `tools/timeline_dump.py` prints it. The export runs from January
2034 and is appended per event from now on; it is never rewritten, resorted or
cleaned up. `docs/replay-policy.md` is the authority on how the timeline is
read, and the desk note is not.

## Consequences

- `docs/replay-policy.md` Appendix B documents the export's fields.
- The ticket system links to the export instead of copying it.
- A question about a quarantine is answered from the export, directly or
  through the printer, and from the policy for anything about duplicates.
