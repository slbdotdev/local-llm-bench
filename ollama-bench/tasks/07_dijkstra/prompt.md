Create `graph.py` in the current directory with a function `shortest_path(graph, src, dst)`.

- `graph` is a dict mapping node -> dict of neighbour -> non-negative integer edge weight, e.g. `{"a": {"b": 1, "c": 4}, "b": {"c": 2}, "c": {}}`. Edges are directed. A node may appear only as a neighbour and be missing as a key; treat it as having no outgoing edges.
- Return a tuple `(cost, path)` where `path` is the list of nodes from `src` to `dst` inclusive and `cost` is the sum of edge weights along it. Use Dijkstra with a heap (`heapq`).
- If `src == dst`, return `(0, [src])`.
- If `dst` is unreachable, return `(None, [])`.
- Raise `KeyError` if `src` is not a node in the graph (neither a key nor a neighbour).

Write a few quick checks of your own and run them with `python`, then reply "done".
