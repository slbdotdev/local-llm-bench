# Ordering review: one long mixed batch

The order review deliberately combines aliases, empty records, rejected
changes, and duplicate accepted keys. The raw source sequence is `z`, `core`,
`z`, `platform`, `svc`, `service`, `a`. The canonical source sequence is
`z`, `platform`, `z`, `platform`, `service`, `service`, `a`, so the outer result
order is `z`, `platform`, `service`, `a`.

Within `z`, the first accepted keys are `b`, `a`, and `latency`; later `b` and
`lat` changes update existing positions. The inner order is therefore
`b`, `a`, `latency`. A rejected first occurrence of `config` does not reserve a
position; a later accepted `cfg` creates it after latency.

Within platform, a source-only record does create the bucket but contributes no
inner key. If it is the first platform record, a later accepted key starts the
entry list at that later point. An alias record does not reset the position map.

The review rejects three output-building patterns: sorting canonical names,
grouping all raw records before folding, and deleting/reinserting an existing
entry during update. All three can produce the right totals while violating the
temporal contract.
