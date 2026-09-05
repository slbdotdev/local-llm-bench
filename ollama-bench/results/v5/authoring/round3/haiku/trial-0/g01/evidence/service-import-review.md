# Service import review: page set S-17

This is a source-side review of a real-shaped service export. It is included as
evidence because the service emits aliases, ordinary edge spaces, mixed key
case, and administrative changes in the same feed. Each page is part of one
ordered batch; the page numbers are documentation, not input fields.

## Page 1

The first page names `svc` and reports `ERR` with delta 6 as `add`, labels
`Incident`, ` incident `, and an empty label. The source bucket is therefore
`service`. The surviving key is `error`, total contribution is 6, occurrences
is 1, and labels are `["incident"]`.

The second change on the page names `REQ` with delta 2 as `hold`, labels
`Waiting`. It creates a second entry, `requests`, with total 0, occurrence 1,
and label `waiting`. The zero is not a reason to omit the entry.

## Page 2

The continuation uses ` service ` and reports `request` with delta -3 as
`remove`, labels `Network`, `network`. Source canonicalization merges the page
with the first bucket. The source-local alias maps `request` to `requests`.
The multiplier is -1, so the contribution is +3. The requests entry becomes
total 3, occurrences 2, labels `["waiting", "network"]`.

The page also carries `error` with delta 10 as `ignore`, label `Secret`. This
change is rejected before key and label handling. It does not change error's
total, count, or labels; `secret` must not leak into the entry.

## Page 3

The exporter sometimes emits `svc` with an empty change list after an API
timeout. It is the same canonical source and does not create a new bucket or
disturb the two existing entry positions. It is still a valid record and would
create the service bucket if it were the first record.

## Review conclusion

This page set validates the sequence source bucket, action policy, key alias,
weighted amount, occurrence, and ordered label merge. It also shows why page
pre-aggregation is incorrect: the hold must remain ahead of a later key and the
administrative label must remain invisible.
