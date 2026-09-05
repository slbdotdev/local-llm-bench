You are working in a fresh task directory containing a collection of files. Find the
meeting record and extract the eight facts from the decisions that were actually
approved. It includes early proposals, objections, action-item discussion, and a final
decision log. Do not turn a proposal into a decision, and do not confuse a discussion
deadline with the committed deadline.

Create exactly one file named `answer.json`, a JSON object with exactly these fields:

`approved_cadence` (string), `budget_cap_usd` (integer), `retention_days` (integer),
`alert_threshold` (string), `decision_owner` (string), `deadline` (string), `room`
(string), and `escalation_code` (string).

Use only stated values. Keep the threshold as written rather than changing its scale,
and keep the budget as whole US dollars. Write valid JSON only, with no extra fields or
explanation.
