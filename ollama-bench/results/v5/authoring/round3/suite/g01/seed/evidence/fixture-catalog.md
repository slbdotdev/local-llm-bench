# Fixture catalog rationale

The fixture catalog is intentionally broader than the short examples in the
project package. It records the combinations used in review so that a future
release change can tell whether it changes source lifecycle, policy, identity,
arithmetic, order, or ownership. The catalog is material for the adapter
because each dimension is independently observable in the returned tree.

Source combinations include every known alias beside its canonical target,
aliases in different first-seen positions, unknown case variants, empty source,
ordinary edge spaces, tabs, and source-only pages. Key combinations include
global aliases, source-local aliases, the same raw key in separate sources,
empty keys, interior spaces, tabs, and rejected first occurrences. Action
combinations include every accepted and rejected action with positive, negative,
zero, cancelling, and very large deltas.

Label combinations include repeated raw spellings, edge spaces, case changes,
empty values, tab values, labels introduced by duplicates, and labels attached
to rejected changes. Order combinations place duplicates after new keys and
place aliases after canonical names. Ownership combinations retain and mutate
input and output trees across repeated calls.

The catalog is not a license to add behavior for malformed dictionaries or
unlisted action names. The valid-input boundary is fixed. It is evidence that
the current release contract must be applied in one left-to-right fold with
separate per-source and per-entry state.

The benchmark checker uses an independent oracle rather than importing this
catalog. The catalog exists so that the authoring record contains the same
cross-source and historical breadth that a solver must reconcile.
