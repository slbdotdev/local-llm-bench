# Operations replay: administrative boundaries

Operations replay is the source of most `ignore`, `void`, and `hold` actions.
The replay service does not strip these before sending a record because source
lifecycle is observable. The reducer must make the bucket before it asks policy
whether a change contributes.

Replay R-1 names `ops` with a `void` change for `error`, delta 9, labels
`internal`. `ops` is not an alias, so it remains `ops`; the result has one empty
bucket. There is no entry and no visible label. A later accepted error change
can create the first entry at that later position.

Replay R-2 repeats `ops` with `error`, delta 4, action `hold`, labels `Review`.
Hold is accepted with multiplier zero. It creates error total 0, occurrence 1,
labels `["review"]`. The earlier void did not reserve the error key position.

Replay R-3 repeats `ops` with `error`, delta 0, action `add`, labels `review`,
`Ready`. Total remains 0 and occurrence becomes 2. The existing review label is
not repeated, and ready is appended. A zero raw delta is not rejected.

Replay R-4 uses `ops` with `error`, delta -2, action `remove`, labels `Fix`.
The contribution is +2; total becomes 2, occurrence 3, labels
`["review", "ready", "fix"]`.

Replay R-5 uses `ops` with `error`, delta 100, action `ignore`, labels `Gone`.
Nothing changes. In particular, `gone` does not append to the existing entry.

The replay's source record and change order are preserved by the batch adapter.
No replay-specific exception changes the general release contract.
