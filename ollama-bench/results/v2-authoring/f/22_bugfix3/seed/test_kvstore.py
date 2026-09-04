import sys
from kvstore import latest_version, put, delete, value_at, snapshot, keys_at, range_query, history

fails = []
def check(name, cond):
    if not cond:
        fails.append(name); print("FAIL:", name)

# --- latest_version / put / delete ---
check("latest empty", latest_version([]) == 0)
log = []
check("put v1", put(log, "a", "1") == 1)
check("put v2", put(log, "b", "2") == 2)
check("delete v3", delete(log, "a") == 3)
check("latest after ops", latest_version(log) == 3)

# --- value_at ---
check("value at exact version", value_at(log, "a", 1) == "1")
check("value before set", value_at(log, "b", 0) is None)
check("value after set", value_at(log, "b", 3) == "2")
check("value after delete", value_at(log, "a", 3) is None)
check("value unknown key", value_at(log, "zz", 3) is None)

# --- snapshot: no state may leak between calls ---
check("snapshot log", snapshot(log, 2) == {"a": "1", "b": "2"})
log2 = []
put(log2, "c", "3")
check("snapshot independent between calls", snapshot(log2, 1) == {"c": "3"})
check("snapshot of empty log", snapshot([], 5) == {})

# --- delete writes a tombstone even for unknown keys ---
log3 = []
delete(log3, "ghost")
check("ghost history", history(log3, "ghost") == [(1, None)])
check("ghost not live", keys_at(log3, 1) == [])

# --- range_query: inclusive bounds, ascending by key ---
log4 = []
put(log4, "b", "1")
put(log4, "a", "2")
put(log4, "z", "5")
put(log4, "m", "4")
check("range sorted by key", range_query(log4, 4, "a", "z") ==
      [("a", "2"), ("b", "1"), ("m", "4"), ("z", "5")])
check("range inclusive hi", range_query(log4, 4, "m", "z") == [("m", "4"), ("z", "5")])
check("range inclusive lo", range_query(log4, 4, "a", "b") == [("a", "2"), ("b", "1")])
check("range empty window", range_query(log4, 4, "n", "x") == [])

# --- keys_at ---
check("keys_at version 0", keys_at(log4, 0) == [])
check("keys_at mid", keys_at(log4, 2) == ["a", "b"])
delete(log4, "b")
check("keys_at after delete", keys_at(log4, 5) == ["a", "m", "z"])

# --- logs may be out of version order ---
manual = [{"version": 3, "op": "set", "key": "x", "value": "9"},
          {"version": 1, "op": "set", "key": "y", "value": "7"}]
check("latest out-of-order", latest_version(manual) == 3)
check("put after out-of-order log", put(manual, "w", "0") == 4)
check("value out-of-order", value_at(manual, "y", 3) == "7")

# --- history ---
h = []
put(h, "k", "1")
put(h, "other", "x")
put(h, "k", "2")
delete(h, "k")
put(h, "k", "3")
check("history", history(h, "k") == [(1, "1"), (3, "2"), (4, None), (5, "3")])

# --- read functions must not modify the log ---
before = list(log4)
snapshot(log4, 5)
keys_at(log4, 5)
range_query(log4, 5, "a", "z")
history(log4, "a")
check("reads do not mutate log", list(log4) == before)

if fails:
    print(f"{len(fails)} failing"); sys.exit(1)
print("ALL OK")