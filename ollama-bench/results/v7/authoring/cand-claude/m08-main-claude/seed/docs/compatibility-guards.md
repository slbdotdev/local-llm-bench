# Compatibility guards

*Which existing test guards which stage's contract against a change elsewhere. Each
row is independent; a stage not listed here guards nothing outside its own tests.*

| a change touching ... | must keep passing ... | because |
| --- | --- | --- |
| `attestation` | `tests/test_shard.py` | it was the first test written against the pair |
| `backfill` | `tests/test_retention.py` | it was the first test written against the pair |
| `cursor` | `tests/test_audit.py` | it was the first test written against the pair |
| `retention` | `tests/test_cursor.py` | it was the first test written against the pair |
| `shard` | `tests/test_lineage.py` | it was the first test written against the pair |
| `watermark` | `tests/test_quota.py` | it is the only test that exercises the contract watermark and quota share |

A compatibility guard is a test that already exists; this document only records
which one a given change must not break. Nothing here is a new test to write.
