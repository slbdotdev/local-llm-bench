# Release-engineering runbook

First identify the requested release month and platform. Then canonicalize the target and every lock dependency, check catalog availability, apply policy, and only then produce the closure. The closure must not contain a package that was merely mentioned in a comment or in a historical note. If any dependency cannot be selected, return the empty plan rather than silently dropping it.

The output is consumed by a byte-oriented deploy step. It has a final newline, uses LF internally, and puts dependencies before their consumers. Package versions come from the lock snapshot, not from the catalog's advisory version.

When debugging, compare a plan's header, canonical target, line order, pinned versions, and the `requires=` spelling independently. A plan that contains the right names in the wrong order is not reproducible.
