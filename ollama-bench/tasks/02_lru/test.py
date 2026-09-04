import sys, time
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    from lru import LRUCache
    c = LRUCache(2)
    c.put(1, 1); c.put(2, 2)
    check("get1", c.get(1) == 1)
    c.put(3, 3)  # evicts 2
    check("evict2", c.get(2) == -1)
    check("keys", list(c.keys()) == [1, 3])
    c.put(4, 4)  # evicts 1
    check("evict1", c.get(1) == -1)
    check("get3", c.get(3) == 3)
    check("get4", c.get(4) == 4)
    check("len", len(c) == 2)
    c.put(3, 30)  # update refreshes
    check("update val", c.get(3) == 30)
    check("keys after update", list(c.keys()) == [4, 3])
    c.put(5, 5)  # evicts 4
    check("evict4", c.get(4) == -1)
    check("keys final", list(c.keys()) == [3, 5])
    try:
        LRUCache(0); fails.append("no ValueError for cap 0")
    except ValueError:
        pass
    c1 = LRUCache(1); c1.put("a", 1); c1.put("b", 2)
    check("cap1", c1.get("a") == -1 and c1.get("b") == 2 and len(c1) == 1)
    big = LRUCache(50000)
    t0 = time.time()
    for i in range(200000):
        big.put(i, i)
        big.get(i - 25000)
    check("perf O(1)", time.time() - t0 < 5)
    check("big len", len(big) == 50000)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:8]); sys.exit(1)
print("PASS")
