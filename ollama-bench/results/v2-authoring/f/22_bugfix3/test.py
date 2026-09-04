import sys, subprocess, hashlib, random
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    with open("test_kvstore.py", "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    check("visible tests untouched", h == "ba3f14cd2ed696ead031fb78ad53c801906a6979b2490d5be0d731c656ddf576")
    r = subprocess.run([sys.executable, "test_kvstore.py"], capture_output=True, text=True, timeout=30)
    check("visible tests pass", r.returncode == 0 and "ALL OK" in r.stdout)
    from kvstore import (latest_version, put, delete, value_at,
                         snapshot, keys_at, range_query, history)

    # ---- hidden checks: out-of-order logs and version numbering ----
    m = [{"version": 5, "op": "set", "key": "p", "value": 50},
         {"version": 2, "op": "del", "key": "q", "value": None},
         {"version": 9, "op": "set", "key": "r", "value": "rr"}]
    check("h latest out-of-order", latest_version(m) == 9)
    check("h put after out-of-order", put(m, "s", 1) == 10)
    check("h value_at picks max version", value_at(m, "p", 10) == 50)
    check("h value_at below all", value_at(m, "r", 8) is None)
    check("h latest empty", latest_version([]) == 0)

    # ---- hidden checks: delete always appends a tombstone ----
    log = []
    v = delete(log, "x")
    check("h delete ghost version", v == 1)
    check("h delete ghost appends", len(log) == 1 and log[0]["op"] == "del"
          and log[0]["key"] == "x" and log[0]["value"] is None)
    put(log, "k", "v")
    delete(log, "k")
    v = delete(log, "k")
    check("h delete twice version", v == 4)
    check("h delete twice tombstones", history(log, "k") == [(2, "v"), (3, None), (4, None)])
    check("h value_at after re-delete", value_at(log, "k", 4) is None)

    # ---- hidden checks: boundaries and statelessness ----
    check("h snapshot version 0", snapshot(log, 0) == {})
    check("h snapshot above latest", snapshot(log, 99) == {})
    check("h value_at version 0", value_at(log, "k", 0) is None)
    check("h range lo>hi", range_query(log, 4, "z", "a") == [])
    g = []
    put(g, "b", 2); put(g, "a", 1); delete(g, "b"); put(g, "b", 22)
    check("h range tuples", range_query(g, 4, "a", "c") == [("a", 1), ("b", 22)])
    check("h range tuple type", all(isinstance(t, tuple) and len(t) == 2
                                    for t in range_query(g, 4, "a", "z")))
    check("h keys_at resurrected", keys_at(g, 4) == ["a", "b"])
    check("h snapshot between calls", snapshot(g, 2) == {"a": 1, "b": 2}
          and snapshot(g, 3) == {"a": 1})
    before = list(g)
    snapshot(g, 4); keys_at(g, 4); range_query(g, 4, "a", "z")
    value_at(g, "b", 4); history(g, "b"); latest_version(g)
    check("h reads do not mutate", list(g) == before)

    # ---- randomised differential test against a brute-force reference ----
    def bf_snapshot(log, version):
        live = {}
        for e in sorted(log, key=lambda e: e["version"]):
            if e["version"] > version:
                break
            if e["op"] == "set":
                live[e["key"]] = e["value"]
            else:
                live.pop(e["key"], None)
        return live

    def bf_value_at(log, key, version):
        bv, b = 0, None
        for e in log:
            if e["key"] == key and e["version"] <= version and e["version"] > bv:
                bv, b = e["version"], e["value"]
        return b

    rng = random.Random(20240707)
    KEYS = ["a", "b", "c", "d", "e"]
    for t in range(50):
        log = []
        for step in range(rng.randint(1, 25)):
            k = rng.choice(KEYS)
            expect = latest_version(log) + 1
            if rng.random() < 0.3:
                rv = delete(log, k)
                check(f"diff t{t} s{step} delete appends tombstone",
                      len(log) >= 1 and log[-1]["op"] == "del" and log[-1]["value"] is None)
            else:
                rv = put(log, k, rng.randint(0, 99))
                check(f"diff t{t} s{step} put appends set",
                      len(log) >= 1 and log[-1]["op"] == "set")
            check(f"diff t{t} s{step} version numbering", rv == expect)
        shuffled = list(log)
        rng.shuffle(shuffled)  # entries may appear in any order
        V = latest_version(shuffled)
        versions = {0, V, V + 1} | {rng.randint(0, V + 1) for _ in range(4)}
        for v in sorted(versions):
            snap = bf_snapshot(shuffled, v)
            check(f"diff t{t} v{v} snapshot", snapshot(shuffled, v) == snap)
            check(f"diff t{t} v{v} keys_at", keys_at(shuffled, v) == sorted(snap))
            lo, hi = rng.choice(KEYS), rng.choice(KEYS)
            check(f"diff t{t} v{v} range",
                  range_query(shuffled, v, lo, hi) ==
                  [(kk, snap[kk]) for kk in sorted(snap) if lo <= kk <= hi])
            k = rng.choice(KEYS)
            check(f"diff t{t} v{v} value_at", value_at(shuffled, k, v) == bf_value_at(shuffled, k, v))
        for k in KEYS:
            check(f"diff t{t} history {k}",
                  history(shuffled, k) ==
                  sorted((e["version"], e["value"]) for e in shuffled if e["key"] == k))
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")