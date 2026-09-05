You are working in a fresh task directory containing a collection of files. Read the
provided technical record carefully; the record is deliberately long and includes
background material, discarded hypotheses, and operational detail. Find the one
authoritative incident record in the available files. Do not infer or calculate facts
that are not stated there.

Create exactly one file named `answer.json` in the current directory. It must be a JSON
object with exactly these eight fields and no others:

`incident_date` (string), `affected_region` (string), `impact_scope` (string),
`detection_channel` (string), `customer_minutes` (integer), `root_cause` (string),
`rollback_build` (string), and `followup_owner` (string).

Use the value supported by the authoritative record, not a nearby estimate, proposal,
or example. Preserve the meaning of units and the distinction between customer impact
and internal timing. JSON must be valid UTF-8 JSON; do not add commentary to the file.
