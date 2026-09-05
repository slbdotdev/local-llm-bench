# Regression ledger

These are the release-review assertions in prose. They are kept beside the
fixtures because each one describes a failure that looked correct in a small
smoke test.

* A source record is visible before policy is consulted. Three rejected changes
  therefore leave one empty canonical bucket.
* `core` followed by `platform` has one `platform` bucket. It stays at the
  position of the first record, even if a later source would sort earlier.
* `compile` is a platform `build` key. The source-specific table is consulted
  after the global table, not before it.
* `WARN`, `warn`, and ` warning ` are one key. A leading tab is not removed.
* A hold with delta 0 is accepted, makes an entry, increments occurrences, and
  may add labels. A zero-valued add has the same count behavior.
* `ignore` and `void` do not create an entry and their labels do not leak into
  an entry created later for the same key.
* A remove multiplies a signed delta by -1. Thus removing -4 contributes +4.
* Duplicate accepted keys update total and occurrence count in place. They do
  not move after a later key is first seen.
* Labels are canonicalized before deduplication. Empty canonical labels vanish;
  the first nonempty canonical label wins its position.
* The returned object is fresh at every list and dictionary layer relevant to
  the public shape. Modifying it after the call cannot change the input.

The release review deliberately includes large integers, cancellation to zero,
empty names, repeated aliases, interspersed rejected changes, and records whose
change list is empty. These combinations are not exceptional modes; they are
the reason the adapter contract is written as an ordered fold.
