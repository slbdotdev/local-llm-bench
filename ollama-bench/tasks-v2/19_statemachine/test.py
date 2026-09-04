import sys, random, inspect, re as _re

fails = []
def check(name, cond):
    if not cond: fails.append(name)

# ---- Independent reference interpreter of the same table (flat rule list) ----
ENTRY = {"IDLE": [], "ONE": ["1"], "TWO": ["2"], "SERVE": ["D"], "OUT": ["O"]}
EXIT = {"IDLE": [], "ONE": [], "TWO": ["x"], "SERVE": ["d"], "OUT": []}

# each rule: (state, event, guard(st) -> bool, target, outputs, side effect)
RULES = [
    ("IDLE", "c", lambda st: True, "ONE", ["A"], None),
    ("ONE", "c", lambda st: True, "TWO", ["A"], None),
    ("ONE", "t", lambda st: st["ticks"] >= 3, "IDLE", ["F"], None),
    ("ONE", "t", lambda st: True, "ONE", ["w"], None),
    ("ONE", "r", lambda st: True, "IDLE", ["F"], None),
    ("TWO", "s", lambda st: st["stock"] > 0, "SERVE", [], "dec_stock"),
    ("TWO", "s", lambda st: True, "OUT", ["F"], None),
    ("TWO", "t", lambda st: st["ticks"] >= 2, "IDLE", ["F"], None),
    ("TWO", "t", lambda st: True, "TWO", ["w"], None),
    ("TWO", "r", lambda st: True, "IDLE", ["F"], None),
    ("SERVE", "c", lambda st: True, "IDLE", [], None),
    ("SERVE", "s", lambda st: True, "IDLE", [], None),
    ("SERVE", "r", lambda st: True, "IDLE", [], None),
    ("SERVE", "t", lambda st: True, "IDLE", [], None),
]

def ref_run(events):
    state = "IDLE"
    st = {"stock": 2, "ticks": 0}
    out = []
    for ev in events:
        if ev == "t":
            st["ticks"] += 1
        else:
            st["ticks"] = 0
        if ev == "z":
            out.extend(EXIT[state])
            out.append("R")
            state = "IDLE"
            continue
        chosen = None
        for (s, e, guard, target, emits, side) in RULES:
            if s == state and e == ev and guard(st):
                chosen = (target, emits, side)
                break
        if chosen is None:
            out.append("E")
            continue
        target, emits, side = chosen
        if side == "dec_stock":
            st["stock"] -= 1
        if target != state:
            out.extend(EXIT[state])
        out.extend(emits)
        if target != state:
            out.extend(ENTRY[target])
        state = target
    return out

# ---- Grader ----
try:
    import machine
    check("has run", hasattr(machine, "run") and callable(machine.run))
    try:
        src = inspect.getsource(machine)
    except Exception:
        src = ""
    check("no time import", not _re.search(r"^\s*(import time\b|from time\b)", src, _re.M))
    check("no threading import", not _re.search(r"^\s*(import threading\b|from threading\b)", src, _re.M))
    check("no random import", not _re.search(r"^\s*(import random\b|from random\b)", src, _re.M))
    F = machine.run

    cases = [
        ([], []),
        (["c"], ["A", "1"]),
        (["c", "c", "s"], ["A", "1", "A", "2", "x", "D"]),
        (["c", "c", "s", "c"], ["A", "1", "A", "2", "x", "D", "d"]),
        (["c", "c", "s", "s"], ["A", "1", "A", "2", "x", "D", "d"]),
        (["c", "c", "s", "r"], ["A", "1", "A", "2", "x", "D", "d"]),
        (["c", "c", "s", "t"], ["A", "1", "A", "2", "x", "D", "d"]),
        (["c", "t", "t", "t"], ["A", "1", "w", "w", "F"]),
        (["c", "t", "t", "t", "t"], ["A", "1", "w", "w", "F", "E"]),
        (["c", "c", "t", "t"], ["A", "1", "A", "2", "w", "x", "F"]),
        (["c", "c", "t", "t", "t", "t"], ["A", "1", "A", "2", "w", "x", "F", "E", "E"]),
        (["c", "t", "c", "t", "t", "t"], ["A", "1", "w", "A", "2", "w", "x", "F", "E"]),
        (["c", "t", "t", "c", "t", "t", "t"], ["A", "1", "w", "w", "A", "2", "w", "x", "F", "E"]),
        (["t", "t", "c", "t", "t"], ["E", "E", "A", "1", "w", "w"]),
        (["c", "c", "c"], ["A", "1", "A", "2", "E"]),
        (["c", "c", "c", "c"], ["A", "1", "A", "2", "E", "E"]),
        (["c", "c", "r"], ["A", "1", "A", "2", "x", "F"]),
        (["c", "r"], ["A", "1", "F"]),
        (["s"], ["E"]),
        (["r"], ["E"]),
        (["t"], ["E"]),
        (["c", "s", "c", "c"], ["A", "1", "E", "A", "2", "E"]),
        (["c", "c", "s", "r", "c", "c", "s", "r", "c", "c", "s"],
         ["A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "F", "O"]),
        (["c", "c", "s", "r", "c", "c", "s", "r", "c", "c", "s", "t"],
         ["A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "F", "O", "E"]),
        (["c", "c", "s", "r", "c", "c", "s", "r", "c", "c", "s", "z", "c", "c", "s"],
         ["A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "F", "O", "R", "A", "1", "A", "2", "x", "F", "O"]),
        (["c", "c", "s", "c", "c", "s", "c", "c", "s"],
         ["A", "1", "A", "2", "x", "D", "d", "A", "1", "E", "A", "2", "E", "x", "D"]),
        (["c", "c", "s", "z", "c", "c", "s"], ["A", "1", "A", "2", "x", "D", "d", "R", "A", "1", "A", "2", "x", "D"]),
        (["z"], ["R"]),
        (["c", "z"], ["A", "1", "R"]),
        (["c", "c", "z"], ["A", "1", "A", "2", "x", "R"]),
        (["c", "c", "c", "z"], ["A", "1", "A", "2", "E", "x", "R"]),
        (["c", "c", "s", "z"], ["A", "1", "A", "2", "x", "D", "d", "R"]),
        (["c", "c", "s", "c", "c", "s", "z"], ["A", "1", "A", "2", "x", "D", "d", "A", "1", "E", "R"]),
        (["q"], ["E"]),
        (["c", "q", "c"], ["A", "1", "E", "A", "2"]),
        (["c", "c", "q", "s"], ["A", "1", "A", "2", "E", "x", "D"]),
    ]
    for evs, want in cases:
        try:
            got = F(evs)
            check(f"{evs!r}", got == want)
            if got != want:
                fails.append(f"  wanted {want}, got {got}")
        except Exception as e:
            fails.append(f"{evs!r} raised {e!r}")
    check("run returns list", isinstance(F(["c"]), list))
    # fresh machine per call / determinism
    a = F(["c", "c", "s"]); b = F(["c", "c", "s"])
    check("stateless across calls", a == b == ["A", "1", "A", "2", "x", "D"])

    # ---- Randomised seeded differential test vs the independent reference ----
    random.seed(1901)
    alphabet = ["c", "c", "c", "s", "s", "r", "r", "t", "t", "t", "t", "z", "q"]
    n = 0
    visited = set()
    for i in range(400):
        evs = [random.choice(alphabet) for _ in range(random.randint(0, 40))]
        want = ref_run(evs)
        try:
            got = F(evs)
        except Exception as e:
            fails.append(f"rand {evs!r} raised {e!r}"); continue
        n += 1
        if got != want:
            fails.append(f"rand {evs!r}: got {got} want {want}")
        if n == 1:
            check("deterministic repeat", F(evs) == got)
    check("enough random cases", n >= 400)
    # coverage of the tricky states: trace the reference over all random sequences
    # coverage of the tricky states: trace the reference over fixed + fresh random sequences
    seqs = [c[0] for c in cases]
    random.seed(1902)
    seqs += [[random.choice(alphabet) for _ in range(random.randint(0, 40))] for _ in range(400)]
    for evs in seqs:
        st_ = "IDLE"; stock = 2; ticks = 0
        visited.add(st_)
        for ev in evs:
            ticks = ticks + 1 if ev == "t" else 0
            if ev == "z":
                st_ = "IDLE"; visited.add("IDLE"); continue
            nxt = None
            for (s, e, guard, target, emits, side) in RULES:
                if s == st_ and e == ev and guard({"ticks": ticks, "stock": stock}):
                    nxt = target
                    if side == "dec_stock": stock -= 1
                    break
            if nxt is None:
                continue
            st_ = nxt
            visited.add(st_)
    for s in ["IDLE", "ONE", "TWO", "SERVE", "OUT"]:
        check(f"coverage {s}", s in visited)
except Exception as e:
    fails.append(f"exception: {e!r}")

if fails:
    print("FAIL", fails[:12]); sys.exit(1)
print("PASS")
sys.exit(0)