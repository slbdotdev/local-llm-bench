You are working in a fresh task directory containing a collection of files. Locate the
long engineering record and extract only the eight requested facts from its signed-off
specification section. The record contains bench observations, superseded settings,
unit conversions, and informal suggestions. Use the final approved value and do not
silently convert or round a value.

Create exactly one file named `answer.json`, a JSON object with exactly these fields:

`rated_payload_kg` (integer), `bus_baud` (integer), `firmware_version` (string),
`validation_date` (string), `enclosure_rating` (string), `calibration_days` (integer),
`approver` (string), and `reserve_voltage` (string).

The values must be stated by the record. In particular, distinguish a test duration
from a maintenance interval and a measured voltage from the required reserve voltage.
Write valid JSON only; no prose or extra fields.
