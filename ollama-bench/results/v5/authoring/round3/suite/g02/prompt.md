# Repair the release planner

The sandbox contains a small `releaseplan` Python package, a seven-shard package
catalog and lock snapshot under `data/`, release-policy and naming-history
documentation under `docs/`, and a test suite under `tests/`. Exactly one test
is failing. Diagnose the localized implementation defect and repair the
implementation so the complete suite passes.

The public operation is `releaseplan.build_plan(catalog_text, lock_text,
policy_text, history_text, target, platform, release)`. It returns a
deterministic LF text plan, or the empty string when the target cannot be
deployed. `plan_records` returns the selected canonical package names. Read
the package code and the project material to determine the exact rules: dated
renames, transitive dependency closure, platform availability, policy
precedence, pinned versions, dependency-first ordering, and byte-stable
rendering all matter. The lock snapshot supplies dependency order and pinned
versions; catalog versions are advisory.

A plan is valid only when every package in the transitive closure exists in
both snapshots, is available on the requested platform, and is allowed by the
active policy. A wildcard policy applies to every platform. The most recent
active revision wins; at a revision tie, an exact platform rule beats a
wildcard. Release windows are half-open. Historical aliases are applied by
effective release month, repeatedly, before lookup. Preserve the documented
output order and formatting.

Make the smallest correct implementation change. Do not edit, delete, weaken,
or replace tests, data, or documentation. Do not add dependencies. Use only
the Python standard library, and do not use the network. Run the suite with:

    python3 tests/test_planner.py

For a one-package catalog and lock containing `app`, empty policy and history,
target `app`, platform `linux`, and release `2025-03`, the result is:

    release=2025-03 platform=linux
    target=app
    - app@1.0 requires=

For the same input with an active deny rule for `app`, the result is the empty
string.
