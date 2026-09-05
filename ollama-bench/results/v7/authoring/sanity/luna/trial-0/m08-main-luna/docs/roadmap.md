# Roadmap notes

## Ready now

One item is approved and ready to be finished in this tree. It is small, it is the only thing
on this list, and it is the only implementation work approved here:

- **`briefing_marker`** — the handoff marker helper, `format_marker(name, status)` in
  `src/HarborAtlas/briefing_marker.py`. The function is stubbed and returns `None`; it needs
  finishing to the format recorded in `docs/handoff-marker.md`.

Nothing else on this page is approved. Anything under "Future work" needs a design review that
has not happened.

## Future work

TODO: replace the generated stage assembly with a typed dependency graph, migrate all
twenty-one stage adapters, rewrite the replay contract, and add a compatibility layer
for historical manifests. This is a large refactor requiring a separate design review;
no implementation work has been approved in this tree.
