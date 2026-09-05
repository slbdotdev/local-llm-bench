# 2024-02 import rewrite

The first batch importer was written against nightly snapshots. It accepted a
flat list of `(source, key, delta)` tuples and emitted sorted counters. When
records became paged dictionaries, the migration preserved the sort because
the snapshot team considered it a presentation detail. The UI team later
demonstrated that it was not a detail: an operator reading a stream expects the
first observed item to remain first after a later update.

The migration review established that the adapter, not its callers, owns
ordering. A caller must be able to pass pages separately or concatenate them
and get the same fold. This is why source buckets are created while records are
visited and key positions are retained while changes are visited. A dictionary
used only as a position map is fine; iterating it to form output is not the
contract.

The same review found that empty records had operational meaning. A source that
reported an empty page had been contacted and must appear in the review result.
The 3.2 release keeps that rule even if the page contains only administrative
changes. A completely empty input still returns a fresh empty list.
