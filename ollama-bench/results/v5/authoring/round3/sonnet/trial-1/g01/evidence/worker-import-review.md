# Worker import review: queue replay W-31

Worker exports use `jobs` and `batch` as source aliases for `worker`. They use
`job` and `task` as source-specific aliases for the `jobs` key. The source is
canonicalized before this local key table is selected. A page containing only
rejected operations still records that worker was contacted.

The first page uses `batch` and reports `task` delta 5 `add`, labels `Queue`,
then `lat` delta 2 `add`, labels `P95`. The result starts with worker entries
`jobs` total 5 count 1 labels `["queue"]`, followed by `latency` total 2 count
1 labels `["p95"]`.

The next page uses `worker` and reports `job` delta 2 `remove`, labels `Done`.
It is the existing jobs key. The contribution is -2, so total 3 and count 2;
labels become `["queue", "done"]`. A remove does not mean “subtract the
absolute amount”; it multiplies the signed input.

The next page uses `jobs` as a source and reports `job` delta -4 `remove`,
labels `Reversed`. The contribution is +4, making jobs total 7 and count 3,
with reversed appended. The negative input is intentional.

The administrative page uses ` batch ` and reports `task` delta 100 `void`,
labels `Internal`. It remains the worker bucket but does not create or update
the jobs entry and never exposes `internal`.

The final page uses `worker` and reports `task` delta 0 `hold`, labels `Zero`.
It updates the existing jobs entry to total 7 and count 4, appending `zero`.
The zero multiplier is accepted; truthiness of either multiplier or delta is
not a policy test. The output key and label order are unchanged by these
updates.
