# relay-north

Operational tooling for the north relay. Two things live here:

- `docs/operations-log.md` — the append-only operations log. Newest entries at the **bottom**.
  Nothing in it is ever rewritten; an entry that turned out to be wrong is corrected by a later
  entry that says so.
- `tools/dump_state.py` — prints the current slot allocation for every stage, one line per slot.
  Run it with `python tools/dump_state.py` from the repository root.

## Reporting a drain

A drain report needs two things: the escalation code currently in force, and the slot number the
`reconcile` stage is currently allocated. The first comes from the log, the second from
`dump_state.py`. Both change, so both are read fresh each time rather than remembered.
