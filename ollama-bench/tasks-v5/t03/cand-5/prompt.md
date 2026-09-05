You are working in a fresh task directory containing a repository snapshot for the Meridian
Relay archive rollout. Read the project material under the supplied tree, including the
current source modules, policy and operations documents, finance/compliance notes, tests,
and the dated history.

Extract the eight facts from the effective, ordinary production baseline for the normalized
delivery ledger. Reconcile the sources in this order: identify the scope of the baseline,
follow the revision and approval status, then use the current component records to obtain
the values and their required representations. Do not treat a proposal, forecast, question,
dashboard display, compatibility fixture, action assignment, legal hold, emergency route,
or rejected change request as an approved baseline value. In particular, a request that is
not both approved and effective must not alter the ordinary baseline. The repository records
why nearby alternatives remain present.

Create exactly one file named `answer.json`, a JSON object with exactly these fields:

`approved_cadence` (string), `budget_cap_usd` (integer), `retention_days` (integer),
`alert_threshold` (string), `decision_owner` (string), `deadline` (string), `room` (string),
and `escalation_code` (string).

Use the normalized values from the effective ordinary baseline. Preserve the threshold's
fraction scale and its string representation; do not turn it into a percentage. Keep the
budget and retention as whole-number JSON integers. Keep the committed date in ISO
year-month-day form, and use the named person and physical verification room rather than
a team, role, building, bridge, or action assignee. Write valid JSON only, with no extra
fields or explanation. JSON object member order is not significant.
