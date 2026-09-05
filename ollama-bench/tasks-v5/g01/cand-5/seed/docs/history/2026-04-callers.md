# 2026-04 caller compatibility pass

The service, build, and operations callers were each replayed against the same
ordered record sequence. The service caller emits `svc`, `web`, and `ui`; the
build caller emits `core`, `jobs`, and `batch`; operations may emit rejected
actions and holds. The adapter output is the shared contract, so callers do no
sorting, alias expansion, action filtering, or label normalization themselves.

The replay was run in page sizes one, two, and five. Flattening pages before the
fold produced the same result as passing the flattened records directly. Any
implementation that reduces each page independently and merges finished
outputs can fail because it may reorder entries or lose a source-only page.

The UI's display assumptions are observable requirements: outer and inner order
are first-seen order; zero totals remain visible when occurrences is nonzero;
labels are lowercase case-folded strings in first-seen order. The UI does not
sort or repair the adapter result.
