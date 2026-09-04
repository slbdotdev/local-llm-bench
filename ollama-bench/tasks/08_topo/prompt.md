Create `deps.py` in the current directory with:

- `class CycleError(ValueError)` whose `.cycle` attribute is a list of nodes forming the cycle (first node repeated at the end, e.g. `["a", "b", "a"]`).
- `resolve(deps: dict[str, list[str]]) -> list[str]`: a build order. `deps[x]` lists the things `x` depends on, which must all come before `x` in the result. Nodes that appear only inside dependency lists must also be included in the output. The result must be deterministic: whenever several nodes are available to emit next, emit the alphabetically smallest first (i.e. Kahn's algorithm with a min-heap).
- If the graph has a cycle, raise `CycleError`.

Examples:
- `resolve({"app": ["lib", "util"], "lib": ["util"]}) == ["util", "lib", "app"]`
- `resolve({"b": [], "a": []}) == ["a", "b"]`
- `resolve({"a": ["b"], "b": ["a"]})` raises `CycleError`.

Write a few quick checks of your own and run them with `python`, then reply "done".
