# Fixture regeneration note

On 2034-07-14, `tools/make_fixtures.py` was used to re-derive the intake journals under `data/intake`
from the source event stream, after the handoff defect in the June drain. The
regeneration is faithful to the source stream: where the stream carries admissions dated
after a stage's recorded close, the journal now carries them too.

Flagged for declaration review at regeneration time: attestation, compaction, cursor, retention, shard.

The closing positions recorded at the end of each stage document predate the
regeneration and are pending re-derivation at the next close. They have not been
re-derived yet.

Stand-up sign-off, 2034-07-15: unit tests green in CI against the regenerated fixtures.
The release verification had not been re-run at the time of sign-off.
