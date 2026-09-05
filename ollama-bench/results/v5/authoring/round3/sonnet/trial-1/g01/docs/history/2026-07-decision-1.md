# 2026-07 decision record: bucket lifecycle

Decision D-41: create a canonical bucket before applying action policy.

Context: an operations feed can contain a source record whose every change is
administrative. The dashboard needs to distinguish that source from one absent
from the feed. Filtering records by accepted changes before the reducer erased
that distinction. The decision was verified with empty lists, rejected-only
lists, and alias records.

Consequences: source normalization is performed once for every record; a new
fresh bucket and its per-source position map are made immediately. Later
changes may add entries, but no rejected change can add an entry. An existing
source record, including an empty one, never resets state. The bucket's position
is the first record position after source canonicalization.

Rejected alternatives: build buckets only on the first accepted change; use raw
source spelling as identity; sort canonical buckets after reduction. Each
alternative produced a superficially tidy JSON snapshot but failed caller
observations and page replay.

This decision interacts with key policy only through sequencing. Source alias
lookup must happen before selecting a local key table, but key canonicalization
must wait until a change has survived policy. The outer lifecycle is therefore
not a reason to inspect or normalize a rejected change's key or labels.
