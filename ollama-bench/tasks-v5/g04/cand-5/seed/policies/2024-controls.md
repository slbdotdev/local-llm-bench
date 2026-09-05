# 2024 controls memo (archived)

The controls team proposed accepting a `captured` row when its `approved_by` field was
present.  The proposal was rejected: a close contains only ledger-posted entries.  A
`void` flag is not the same thing as a posted state, and a posted row with a later void
marker is excluded by the current feed contract.

The 2024 report rounded native amounts to whole units before conversion.  That was a
known defect and must not be reproduced in the current report.
