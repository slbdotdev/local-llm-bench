# Release plan format

A plan starts with the release and platform header, then the canonical target, then one dependency-first line per selected package. The lock snapshot supplies versions and dependency spelling. A blank plan means that the target is absent, unavailable, denied, or depends on anything that is absent, unavailable, or denied.

Catalog records describe what can run. A platform list containing `*` applies everywhere. A lock dependency list is ordered input; the output must be dependency-first and deterministic. Do not sort independent packages by version: the traversal order from the lock snapshot is part of the reproducible release record.

The renderer preserves the dependency list after `requires=` exactly as supplied by the lock snapshot. Canonical names are used in the header and package line, while the pinned lock version is authoritative.
