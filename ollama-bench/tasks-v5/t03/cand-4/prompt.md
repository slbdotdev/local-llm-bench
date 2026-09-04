You are working in a fresh task directory containing a collection of records. Find the
authoritative, signed release decision and extract the approved values from it. The
records include operational observations, rejected settings, copied dashboard values,
and follow-up discussion. A value that was measured, proposed, or used in a different
environment is not necessarily an approved value. Prefer the signed decision when
sources disagree.

Create exactly one file named `answer.json` in the current directory. It must be valid
UTF-8 JSON: one object with exactly these ten fields and no others:

`release_train` (string), `approved_mode` (string), `packet_limit_bytes` (integer),
`retry_budget` (integer), `rollout_date` (string), `rollback_trigger` (string),
`decision_owner` (string), `review_window` (string), `audit_retention_days` (integer),
and `external_ticket` (string).

Use the values exactly as stated, preserving units, scale, date form, and the distinction
between a limit, an observation, a duration, and a retention policy. For
`external_ticket`, record the authoritative ticket status, including an explicit
absence or not-assigned status if that is what the decision says. Do not infer a value
from an identifier that merely looks like a ticket. Do not add explanation or extra
fields to the file.
