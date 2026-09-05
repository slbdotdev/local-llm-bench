# admission policy

*Owner: S. Nwachukwu (Client Integrations). Module: `src/admission_policy.py`.*

## What it is for

The admission policy describes the handoff boundary for the CedarSignal pipeline. It
keeps a bounded set of records while a downstream acknowledgement is pending.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the largest number of handoff records held before admission refuses new work |
| `window_s` | 60 | seconds a handoff record may stay `pending` before it is reaped |

## States

- `pending` - accepted, not yet acted on
- `queued` - held while awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
