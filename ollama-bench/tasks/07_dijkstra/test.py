import sys, random, heapq, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)

def ref(graph, src, dst):
    nodes = set(graph) | {n for d in graph.values() for n in d}
    if src not in nodes: raise KeyError(src)
    dist = {src: 0}; pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")): continue
        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return dist.get(dst)

def valid_path(graph, src, dst, cost, path):
    if not path or path[0] != src or path[-1] != dst: return False
    total = 0
    for a, b in zip(path, path[1:]):
        if b not in graph.get(a, {}): return False
        total += graph[a][b]
    return total == cost

try:
    import graph as G
    check("uses heapq", "heapq" in inspect.getsource(G))
    g = {"a": {"b": 1, "c": 4}, "b": {"c": 2, "d": 5}, "c": {"d": 1}, "d": {}}
    check("basic", G.shortest_path(g, "a", "d") == (4, ["a", "b", "c", "d"]))
    check("same node", G.shortest_path(g, "b", "b") == (0, ["b"]))
    check("unreachable", G.shortest_path(g, "d", "a") == (None, []))
    check("neighbour-only node", G.shortest_path({"a": {"b": 3}}, "a", "b") == (3, ["a", "b"]))
    check("neighbour-only src", G.shortest_path({"a": {"b": 3}}, "b", "a") == (None, []))
    try:
        G.shortest_path(g, "zz", "a"); fails.append("no KeyError")
    except KeyError:
        pass
    check("zero weight", G.shortest_path({"a": {"b": 0}, "b": {"c": 0}}, "a", "c") == (0, ["a", "b", "c"]))
    random.seed(3)
    for i in range(40):
        n = random.randint(3, 12)
        names = [f"n{k}" for k in range(n)]
        gg = {x: {} for x in names}
        for _ in range(random.randint(n, 3 * n)):
            u, v = random.sample(names, 2); gg[u][v] = random.randint(0, 9)
        s, t = random.sample(names, 2)
        want = ref(gg, s, t)
        got = G.shortest_path(gg, s, t)
        if want is None:
            check(f"rand {i} unreachable", got == (None, []))
        else:
            check(f"rand {i}", isinstance(got, tuple) and len(got) == 2 and got[0] == want and valid_path(gg, s, t, got[0], list(got[1])))
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
