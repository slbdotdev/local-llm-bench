# The drain ceiling currently in force

You are working in a checkout of the earing-mesh repository; your current directory is the root
of that checkout.

`docs/operations-ledger.md` is an append-only ledger. Somewhere in it is a line reading
`CURRENT_DRAIN_CEILING = <number>`, and the line immediately above it is a date. The file is
larger than one read can return, and it contains more than one such line: one block is marked as
superseded and retained only for audit, and exactly one entry is in force.

Report the ceiling that is currently in force, and the date on the line immediately above it.

Write your answer to a new file `ceiling.txt` in the root of the workspace. Give one
`key: value` line for each of these two keys, in any order:

    ceiling: the number currently in force, as a plain integer
    as_of:   the date on the line above it, exactly as the ledger writes it

Nothing else in the file. Do not modify or delete any existing file, and create no file other
than `ceiling.txt`.
