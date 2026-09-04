import sys, os, json, random, threading, subprocess

TOTAL = 36
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()

try:
    import spanmap
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _Missing(object):
    def __init__(self, *a, **k):
        raise AttributeError("attribute missing from spanmap")


SM = getattr(spanmap, "SpanMap", _Missing)
SE = getattr(spanmap, "SpanError", None)


def M(*ops):
    """Build a SpanMap by applying ('p', lo, hi, label) / ('e', lo, hi) ops."""
    m = SM()
    for op in ops:
        if op[0] == "p":
            m.paint(op[1], op[2], op[3])
        else:
            m.erase(op[1], op[2])
    return m


def kind_of(fn):
    """Return the .kind of the SpanError raised by fn(), or a marker string."""
    if not (isinstance(SE, type) and issubclass(SE, BaseException)):
        return "<no SpanError>"
    try:
        fn()
    except SE as e:
        return getattr(e, "kind", "<no .kind>")
    except Exception as e:
        return "<%s>" % type(e).__name__
    return "<no raise>"


def kinds(pairs):
    """pairs: list of (thunk, expected_kind)."""
    def probe():
        for fn, want in pairs:
            if kind_of(fn) != want:
                return False
        return True
    return probe


# --- 1: exception type -------------------------------------------------
check("SpanError subclasses ValueError",
      lambda: isinstance(SE, type) and issubclass(SE, ValueError))

# --- 2-10: paint / spans canonicalisation ------------------------------
check("empty map",
      lambda: M().spans() == [] and M().labels() == {} and M().covered() == 0
      and M().at(0) is None and M().slice(-5, 5) == [])
check("single paint, at() boundaries, covered()",
      lambda: M(("p", 0, 10, "a")).spans() == [(0, 10, "a")]
      and M(("p", 0, 10, "a")).at(0) == "a"
      and M(("p", 0, 10, "a")).at(9) == "a"
      and M(("p", 0, 10, "a")).at(10) is None
      and M(("p", 0, 10, "a")).at(-1) is None
      and M(("p", 0, 10, "a")).covered() == 10)
check("interior paint splits a span",
      lambda: M(("p", 0, 10, "a"), ("p", 3, 5, "b")).spans()
      == [(0, 3, "a"), (3, 5, "b"), (5, 10, "a")])
check("interior repaint with the same label re-merges",
      lambda: M(("p", 0, 10, "a"), ("p", 3, 5, "b"), ("p", 3, 5, "a")).spans()
      == [(0, 10, "a")]
      and M(("p", 0, 10, "a"), ("p", 3, 5, "b"), ("p", 2, 7, "a")).spans()
      == [(0, 10, "a")])
check("adjacent equal labels merge",
      lambda: M(("p", 0, 5, "a"), ("p", 5, 10, "a")).spans() == [(0, 10, "a")]
      and M(("p", 5, 10, "a"), ("p", 0, 5, "a")).spans() == [(0, 10, "a")]
      and M(("p", 0, 2, "a"), ("p", 4, 6, "a"), ("p", 2, 4, "a")).spans()
      == [(0, 6, "a")])
check("paint exactly over an existing span",
      lambda: M(("p", 0, 10, "a"), ("p", 0, 10, "b")).spans() == [(0, 10, "b")]
      and M(("p", 0, 10, "a"), ("p", 0, 10, "a")).spans() == [(0, 10, "a")]
      and M(("p", 0, 4, "a"), ("p", 4, 8, "b"), ("p", 4, 8, "a")).spans()
      == [(0, 8, "a")])
check("paint covering several whole spans",
      lambda: M(("p", 0, 2, "a"), ("p", 4, 6, "b"), ("p", 8, 10, "c"),
                ("p", 0, 10, "z")).spans() == [(0, 10, "z")]
      and M(("p", 0, 2, "a"), ("p", 4, 6, "b"), ("p", 8, 10, "c"),
            ("p", 1, 9, "z")).spans()
      == [(0, 1, "a"), (1, 9, "z"), (9, 10, "c")])
check("paint spanning partial ends of two spans",
      lambda: M(("p", 0, 5, "a"), ("p", 5, 10, "b"), ("p", 3, 7, "c")).spans()
      == [(0, 3, "a"), (3, 7, "c"), (7, 10, "b")])
check("paint with hi == lo is a no-op; order of paints does not matter",
      lambda: M(("p", 4, 4, "a")).spans() == []
      and M(("p", 0, 10, "a"), ("p", 5, 5, "b")).spans() == [(0, 10, "a")]
      and M(("p", 10, 20, "b"), ("p", 0, 5, "a"), ("p", -5, -1, "c")).spans()
      == [(-5, -1, "c"), (0, 5, "a"), (10, 20, "b")])

# --- 11-14: erase ------------------------------------------------------
check("erase inside a span splits it",
      lambda: M(("p", 0, 10, "a"), ("e", 4, 6)).spans()
      == [(0, 4, "a"), (6, 10, "a")]
      and M(("p", 0, 10, "a"), ("e", 4, 6)).covered() == 8)
check("erase exactly a span, and one span among others",
      lambda: M(("p", 0, 10, "a"), ("e", 0, 10)).spans() == []
      and M(("p", 0, 2, "a"), ("p", 4, 6, "b"), ("e", 4, 6)).spans()
      == [(0, 2, "a")]
      and M(("p", 0, 5, "a"), ("p", 5, 10, "a"), ("e", 0, 5)).spans()
      == [(5, 10, "a")])
check("erase spanning several spans partially",
      lambda: M(("p", 0, 4, "a"), ("p", 4, 8, "b"), ("p", 8, 12, "c"),
                ("e", 2, 10)).spans() == [(0, 2, "a"), (10, 12, "c")]
      and M(("p", 0, 4, "a"), ("p", 6, 10, "b"), ("e", 3, 7)).spans()
      == [(0, 3, "a"), (7, 10, "b")])
check("erase no-op cases and erasing everything",
      lambda: M(("p", 0, 10, "a"), ("e", 5, 5)).spans() == [(0, 10, "a")]
      and M(("p", 0, 10, "a"), ("e", 20, 30)).spans() == [(0, 10, "a")]
      and M(("e", 0, 10)).spans() == []
      and M(("p", 0, 4, "a"), ("p", 6, 9, "b"), ("e", -100, 100)).spans() == []
      and M(("p", 0, 4, "a"), ("e", -100, 100)).labels() == {}
      and M(("p", 0, 4, "a"), ("e", -100, 100)).covered() == 0)

# --- 15: at() ----------------------------------------------------------
check("at() over gaps and negative coordinates",
      lambda: [M(("p", -6, -2, "a"), ("p", 0, 3, "b")).at(p)
               for p in (-7, -6, -3, -2, -1, 0, 2, 3)]
      == [None, "a", "a", None, None, "b", "b", None])

# --- 16-17: slice ------------------------------------------------------
check("slice clips to the window",
      lambda: M(("p", 0, 10, "a")).slice(3, 7) == [(3, 7, "a")]
      and M(("p", 0, 4, "a"), ("p", 4, 8, "b")).slice(2, 6)
      == [(2, 4, "a"), (4, 6, "b")]
      and M(("p", 0, 4, "a"), ("p", 4, 8, "b")).slice(0, 8)
      == [(0, 4, "a"), (4, 8, "b")]
      and M(("p", 0, 4, "a"), ("p", 6, 10, "b")).slice(3, 7)
      == [(3, 4, "a"), (6, 7, "b")])


def slice_edges():
    m = M(("p", 0, 10, "a"))
    if m.slice(10, 20) != [] or m.slice(-20, 0) != []:
        return False
    if m.slice(5, 5) != [] or m.slice(-100, 100) != [(0, 10, "a")]:
        return False
    if m.slice(0, 1) != [(0, 1, "a")] or m.slice(9, 10) != [(9, 10, "a")]:
        return False
    return m.spans() == [(0, 10, "a")] and m.covered() == 10


check("slice edge windows and slice does not mutate", slice_edges)

# --- 18-19: labels / covered ------------------------------------------
check("labels() totals",
      lambda: M(("p", 0, 10, "a"), ("p", 3, 5, "b")).labels() == {"a": 8, "b": 2}
      and M(("p", 0, 10, "a"), ("p", 0, 10, "b")).labels() == {"b": 10}
      and M(("p", 0, 4, "a"), ("p", 10, 14, "a")).labels() == {"a": 8})
check("covered() after mixed operations",
      lambda: M(("p", 0, 10, "a"), ("p", 20, 30, "b"), ("e", 5, 25)).covered() == 10
      and M(("p", 0, 10, "a"), ("p", 5, 15, "b")).covered() == 15
      and M(("p", -5, 5, "a")).covered() == 10)

# --- 20-24: checkpoints -----------------------------------------------


def cp_basic():
    m = M(("p", 0, 10, "a"))
    m.checkpoint()
    m.paint(2, 4, "b")
    if m.spans() != [(0, 2, "a"), (2, 4, "b"), (4, 10, "a")]:
        return False
    m.rollback()
    return m.spans() == [(0, 10, "a")] and m.covered() == 10


def cp_nested():
    m = M(("p", 0, 10, "a"))
    m.checkpoint()
    m.paint(2, 4, "b")
    m.checkpoint()
    m.erase(0, 10)
    m.checkpoint()
    m.paint(50, 60, "z")
    if m.spans() != [(50, 60, "z")]:
        return False
    m.rollback()
    if m.spans() != []:
        return False
    m.rollback()
    if m.spans() != [(0, 2, "a"), (2, 4, "b"), (4, 10, "a")]:
        return False
    m.rollback()
    return m.spans() == [(0, 10, "a")]


def cp_commit():
    m = M(("p", 0, 4, "a"))
    m.checkpoint()
    m.paint(4, 8, "b")
    m.commit()
    if m.spans() != [(0, 4, "a"), (4, 8, "b")]:
        return False
    m2 = M(("p", 0, 4, "a"))
    m2.checkpoint()          # outer
    m2.paint(4, 8, "b")
    m2.checkpoint()          # inner
    m2.paint(8, 12, "c")
    m2.commit()              # inner change kept
    if m2.spans() != [(0, 4, "a"), (4, 8, "b"), (8, 12, "c")]:
        return False
    m2.rollback()            # back to the outer checkpoint
    return m2.spans() == [(0, 4, "a")]


def cp_after_rollback():
    m = SM()
    m.paint(0, 10, "a")
    m.checkpoint()
    m.paint(3, 5, "b")
    m.rollback()
    m.paint(5, 10, "a")
    if m.spans() != [(0, 10, "a")]:
        return False
    m.checkpoint()
    m.erase(2, 8)
    if m.spans() != [(0, 2, "a"), (8, 10, "a")]:
        return False
    m.rollback()
    m.paint(4, 6, "b")
    if m.spans() != [(0, 4, "a"), (4, 6, "b"), (6, 10, "a")]:
        return False
    m.paint(4, 6, "a")
    return m.spans() == [(0, 10, "a")] and m.labels() == {"a": 10}


check("checkpoint + rollback", cp_basic)
check("checkpoints nest three deep", cp_nested)
check("commit keeps changes; later rollback uses the outer checkpoint", cp_commit)
check("map behaves correctly after a rollback", cp_after_rollback)


def no_cp():
    m = SM()
    if kind_of(m.rollback) != "no_checkpoint":
        return False
    if kind_of(m.commit) != "no_checkpoint":
        return False
    m.checkpoint()
    m.rollback()
    if kind_of(m.rollback) != "no_checkpoint":
        return False
    m.checkpoint()
    m.commit()
    return kind_of(m.commit) == "no_checkpoint"


check("rollback/commit without a checkpoint raise kind 'no_checkpoint'", no_cp)

# --- 25-30: error kinds and precedence ---------------------------------
check("kind 'type' for non-int coordinates and non-str label",
      kinds([(lambda: SM().paint("0", 5, "a"), "type"),
             (lambda: SM().paint(0, 5.0, "a"), "type"),
             (lambda: SM().paint(0, 5, 7), "type"),
             (lambda: SM().paint(0, 5, None), "type"),
             (lambda: SM().erase(None, 5), "type"),
             (lambda: SM().at("3"), "type"),
             (lambda: SM().slice(0, "5"), "type")]))
check("bool coordinates are rejected with kind 'type'",
      kinds([(lambda: SM().paint(True, 5, "a"), "type"),
             (lambda: SM().paint(0, False, "a"), "type"),
             (lambda: SM().erase(0, True), "type"),
             (lambda: SM().at(True), "type"),
             (lambda: SM().slice(False, 5), "type")]))
check("kind 'label' for the empty label",
      kinds([(lambda: SM().paint(0, 5, ""), "label"),
             (lambda: SM().paint(3, 3, ""), "label")]))
check("kind 'order' when hi < lo",
      kinds([(lambda: SM().paint(5, 1, "a"), "order"),
             (lambda: SM().erase(5, 1), "order"),
             (lambda: SM().slice(0, -1), "order"),
             (lambda: SM().paint(-1, -5, "a"), "order")]))
check("precedence: label is checked before order",
      kinds([(lambda: SM().paint(5, 1, ""), "label"),
             (lambda: SM().paint(0, -10, ""), "label")]))
check("precedence: type is checked before label and order",
      kinds([(lambda: SM().paint("a", 1, ""), "type"),
             (lambda: SM().paint(5, 1, 3), "type"),
             (lambda: SM().paint(True, 1, ""), "type"),
             (lambda: SM().erase(5.5, 1), "type")]))

# --- 31-33: randomised differential tests ------------------------------
LO, HI = -20, 40


def canon(cells):
    out = []
    for p in range(LO, HI):
        c = cells.get(p)
        if c is None:
            continue
        if out and out[-1][1] == p and out[-1][2] == c:
            out[-1] = (out[-1][0], p + 1, c)
        else:
            out.append((p, p + 1, c))
    return out


def model_labels(cells):
    d = {}
    for v in cells.values():
        d[v] = d.get(v, 0) + 1
    return d


def differential(seed, steps, p_paint, p_erase, use_cp):
    def probe():
        rng = random.Random(seed)
        m = SM()
        cells = {}
        stack = []
        for _step in range(steps):
            a = rng.randint(LO, HI)
            b = rng.randint(LO, HI)
            lo, hi = min(a, b), max(a, b)
            r = rng.random()
            if r < p_paint:
                lab = rng.choice(["x", "y", "z"])
                m.paint(lo, hi, lab)
                for p in range(lo, hi):
                    cells[p] = lab
            elif r < p_paint + p_erase:
                m.erase(lo, hi)
                for p in range(lo, hi):
                    cells.pop(p, None)
            elif r < p_paint + p_erase + 0.12:
                m.checkpoint()
                stack.append(dict(cells))
            elif r < p_paint + p_erase + 0.24:
                if stack:
                    m.rollback()
                    cells = stack.pop()
            else:
                if stack:
                    m.commit()
                    stack.pop()
            want = canon(cells)
            if m.spans() != want:
                return False
            if m.covered() != len(cells):
                return False
            if m.labels() != model_labels(cells):
                return False
            q = rng.randint(LO - 3, HI + 3)
            if m.at(q) != cells.get(q):
                return False
            want_slice = ([(max(x, lo), min(y, hi), l) for x, y, l in want
                           if x < hi and y > lo] if hi > lo else [])
            if m.slice(lo, hi) != want_slice:
                return False
        return True
    return probe


check("randomised differential test A (paint/erase mix)",
      differential(101, 400, 0.55, 0.45, False))
check("randomised differential test B (erase heavy)",
      differential(202, 400, 0.30, 0.70, False))
check("randomised differential test C (with checkpoints)",
      differential(303, 400, 0.42, 0.22, True))

# --- 34-36: performance (subprocess) -----------------------------------
PERF = r'''
import time, json
import spanmap
t = time.time()
m = spanmap.SpanMap()
N = 150000
for i in range(N):
    m.paint(i * 1000, i * 1000 + 600, "a" if i % 2 == 0 else "b")
base = (N - 2000) * 1000
x = 12345
for _k in range(50000):
    x = (x * 1103515245 + 12345) % 2000000
    m.paint(base + x, base + x + 300, "c")
s = m.spans()
el = time.time() - t
chk = 0
for a, b, l in s:
    chk = (chk * 1000003 + a * 7 + b * 11 + ord(l[0])) % (2 ** 61 - 1)
print(json.dumps({"elapsed": el, "n": len(s), "cov": m.covered(),
                  "first": list(s[0]), "last": list(s[-1]),
                  "chk": chk, "labels": m.labels()}), flush=True)
'''
EXP = {"n": 150163, "cov": 90015905, "first": [0, 600, "a"],
       "last": [149999000, 149999600, "b"], "chk": 1870646185202432852,
       "labels": {"a": 44988165, "b": 44988440, "c": 39300}}
perf = {}
try:
    r = subprocess.run([sys.executable, "-c", PERF], capture_output=True,
                       text=True, timeout=20)
    for line in (r.stdout or "").splitlines():
        try:
            perf = json.loads(line)
        except Exception:
            pass
except Exception:
    perf = {}

check("performance: 200k paints + spans() under 5 seconds",
      lambda: isinstance(perf.get("elapsed"), float) and perf["elapsed"] < 5.0)
check("performance workload: span count and covered length correct",
      lambda: perf.get("n") == EXP["n"] and perf.get("cov") == EXP["cov"]
      and perf.get("first") == EXP["first"] and perf.get("last") == EXP["last"])
check("performance workload: exact spans and labels correct",
      lambda: perf.get("chk") == EXP["chk"] and perf.get("labels") == EXP["labels"])

_t.cancel()
report()
