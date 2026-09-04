"""Hidden grader for 57_stateful: framed-protocol session replay.

The oracle below (`_ora_*`) is an independent naive simulator: it deframes by splitting the
raw stream on FLAG bytes into whole segments up front, then runs a flat loop over the
resulting record list with all session state held in one plain dict.
"""
import sys, os, re, random, threading, inspect

TOTAL = 26
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
    import stateful
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

FLAG = 0x7E
ESC = 0x7D
TYPES = {1: "HELLO", 2: "DATA", 3: "PING", 4: "CLOSE", 5: "RESET"}
KEYS = ("state", "clock", "expect", "deadline", "window", "delivered",
        "illegal", "frames", "aborted", "events")


class _MissingErr(Exception):
    pass


PE = getattr(stateful, "ProtocolError", None)
if not (isinstance(PE, type) and issubclass(PE, BaseException)):
    PE = _MissingErr


# =====================================================================
# oracle: phase 1, split the whole stream on FLAG and decode each segment
# =====================================================================
class _OraErr(Exception):
    def __init__(self, kind, index, events):
        Exception.__init__(self, kind)
        self.kind = kind
        self.index = index
        self.events = list(events)


def _ora_seg(seg, has_next):
    n = len(seg)
    pos = 0
    vals = []
    need = 1
    while len(vals) < need:
        if pos >= n:
            return ("drop", "truncated", pos)
        b = seg[pos]
        if b == ESC:
            if pos + 1 >= n:
                return ("drop", "bad_escape" if has_next else "truncated", pos + 1)
            vals.append(seg[pos + 1] ^ 0x20)
            pos += 2
        else:
            vals.append(b)
            pos += 1
        if len(vals) == 1:
            if vals[0] > 8:
                return ("drop", "bad_length", pos)
            need = 5 + vals[0]
    ln, ty, seq, tick = vals[0], vals[1], vals[2], vals[3]
    pay = bytes(vals[4:4 + ln])
    ck = vals[4 + ln]
    if ck != (ln + ty + seq + tick + sum(pay)) & 0xFF:
        return ("drop", "bad_checksum", pos)
    return ("frame", ty, seq, tick, pay, pos)


def _ora_deframe(data):
    recs = []
    parts = bytes(data).split(bytes([FLAG]))
    if parts[0]:
        recs.append(("junk", len(parts[0])))
    for k in range(1, len(parts)):
        seg = parts[k]
        r = _ora_seg(seg, k < len(parts) - 1)
        if r[0] == "drop":
            recs.append(("drop", k - 1, r[1]))
            left = len(seg) - r[2]
        else:
            recs.append(("frame", k - 1, r[1], r[2], r[3], r[4]))
            left = len(seg) - r[5]
        if left > 0:
            recs.append(("junk", left))
    return recs


# =====================================================================
# oracle: phase 2, flat loop over the records
# =====================================================================
def _ora_replay(data, strict=False):
    if type(data) is not bytes and type(data) is not bytearray:
        raise _OraErr("bad_transcript", -1, [])
    S = {"state": "IDLE", "clock": 0, "expect": 0, "deadline": None, "illegal": 0,
         "frames": 0, "aborted": False}
    buf = {}
    delivered = []
    ev = []

    def emit(e):
        if strict and e[0] in ("drop", "illegal", "timeout", "abort"):
            if e[0] == "drop":
                raise _OraErr(e[2], e[1], ev)
            if e[0] == "illegal":
                raise _OraErr("illegal", e[1], ev)
            if e[0] == "timeout":
                raise _OraErr("timeout", -1, ev)
            raise _OraErr(e[1], -1, ev)
        ev.append(e)

    def order():
        return [(S["expect"] + d) % 16 for d in range(16)
                if (S["expect"] + d) % 16 in buf]

    def goto(s):
        if s != S["state"]:
            S["state"] = s
            ev.append(("state", s))
            if s in ("IDLE", "CLOSED"):
                S["deadline"] = None

    def discard():
        for s in order():
            ev.append(("discard", s))
        buf.clear()

    for rec in _ora_deframe(data):
        if S["aborted"]:
            break
        if rec[0] == "junk":
            ev.append(rec)
            continue
        S["frames"] += 1
        if rec[0] == "drop":
            emit(rec)
            continue
        idx, ty, seq, tick, pay = rec[1], rec[2], rec[3], rec[4], rec[5]
        S["clock"] += tick % 64
        if S["deadline"] is not None and S["clock"] > S["deadline"]:
            emit(("timeout", S["clock"]))
            goto("CLOSED")
            discard()
        if ty not in TYPES:
            emit(("drop", idx, "bad_type"))
            continue
        nm = TYPES[ty]
        st = S["state"]
        bad = False
        if nm == "RESET":
            ev.append(("reset", idx))
            goto("IDLE")
            S["deadline"] = None
            S["expect"] = 0
            discard()
        elif nm == "HELLO":
            if st != "IDLE":
                bad = True
            else:
                S["expect"] = seq % 16
                ev.append(("hello", idx, S["expect"]))
                goto("OPEN")
                S["deadline"] = S["clock"] + 20
        elif nm == "PING":
            if st not in ("OPEN", "DRAINING"):
                bad = True
            else:
                ev.append(("ping", idx))
                S["deadline"] = S["clock"] + 20
        elif nm == "CLOSE":
            if st == "OPEN":
                ev.append(("close", idx))
                goto("DRAINING")
                seen = order()
                for s in seen:
                    delivered.append(buf.pop(s))
                    ev.append(("flush", s))
                if seen:
                    S["expect"] = (seen[-1] + 1) % 16
                S["deadline"] = S["clock"] + 20
            elif st == "DRAINING":
                ev.append(("close", idx))
                goto("CLOSED")
            else:
                bad = True
        else:  # DATA
            if st == "DRAINING":
                emit(("drop", idx, "draining"))
            elif st != "OPEN":
                bad = True
            else:
                q = seq % 16
                d = (q - S["expect"]) % 16
                if d == 0:
                    delivered.append(pay)
                    ev.append(("deliver", idx, q))
                    S["expect"] = (S["expect"] + 1) % 16
                    while S["expect"] in buf:
                        delivered.append(buf.pop(S["expect"]))
                        ev.append(("flush", S["expect"]))
                        S["expect"] = (S["expect"] + 1) % 16
                    S["deadline"] = S["clock"] + 20
                elif d <= 3:
                    if q in buf:
                        ev.append(("dup", idx, q))
                    else:
                        buf[q] = pay
                        ev.append(("buf", idx, q))
                        S["deadline"] = S["clock"] + 20
                elif d >= 12:
                    ev.append(("dup", idx, q))
                else:
                    emit(("drop", idx, "out_of_window"))
        if bad:
            emit(("illegal", idx, ty, st))
            S["illegal"] += 1
            if S["illegal"] >= 3:
                S["aborted"] = True
                emit(("abort", "illegal_limit"))
                goto("CLOSED")
    return {"state": S["state"], "clock": S["clock"], "expect": S["expect"],
            "deadline": S["deadline"], "window": [(q, buf[q]) for q in order()],
            "delivered": list(delivered), "illegal": S["illegal"],
            "frames": S["frames"], "aborted": S["aborted"], "events": ev}


# =====================================================================
# wire builders (grader side only)
# =====================================================================
def esc_bytes(body):
    out = bytearray()
    for b in body:
        if b in (FLAG, ESC):
            out += bytes([ESC, b ^ 0x20])
        else:
            out.append(b)
    return bytes(out)


def F(ty, seq, tick, payload=b"", ln=None, ck=None):
    p = bytes(payload)
    L = len(p) if ln is None else ln
    body = bytes([L & 0xFF, ty & 0xFF, seq & 0xFF, tick & 0xFF]) + p
    body += bytes([(sum(body) & 0xFF) if ck is None else (ck & 0xFF)])
    return bytes([FLAG]) + esc_bytes(body)


# =====================================================================
# defensive comparison
# =====================================================================
class _Bad(Exception):
    pass


def _as_bytes(v):
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    raise _Bad()


def _as_int(v):
    if isinstance(v, bool) or not isinstance(v, int):
        raise _Bad()
    return v


def _norm(got):
    """Lenient normalisation, so pure-semantics buckets do not double-punish form."""
    if not isinstance(got, dict):
        raise _Bad()
    for k in KEYS:
        if k not in got:
            raise _Bad()
    out = {}
    if not isinstance(got["state"], str):
        raise _Bad()
    out["state"] = got["state"]
    out["clock"] = _as_int(got["clock"])
    out["expect"] = _as_int(got["expect"])
    out["illegal"] = _as_int(got["illegal"])
    out["frames"] = _as_int(got["frames"])
    d = got["deadline"]
    out["deadline"] = None if d is None else _as_int(d)
    if not isinstance(got["aborted"], (bool, int)):
        raise _Bad()
    out["aborted"] = bool(got["aborted"])
    w = got["window"]
    if isinstance(w, dict):
        pairs = [(_as_int(a), _as_bytes(b)) for a, b in w.items()]
    elif isinstance(w, (list, tuple)):
        pairs = []
        for it in w:
            if not isinstance(it, (list, tuple)) or len(it) != 2:
                raise _Bad()
            pairs.append((_as_int(it[0]), _as_bytes(it[1])))
    else:
        raise _Bad()
    e = out["expect"]
    out["window"] = sorted(pairs, key=lambda kv: (kv[0] - e) % 16)
    dl = got["delivered"]
    if not isinstance(dl, (list, tuple)):
        raise _Bad()
    out["delivered"] = [_as_bytes(x) for x in dl]
    evs = got["events"]
    if not isinstance(evs, (list, tuple)):
        raise _Bad()
    ne = []
    for ev in evs:
        if not isinstance(ev, (list, tuple)):
            raise _Bad()
        ne.append(tuple(ev))
    out["events"] = ne
    return out


def _norm_want(want):
    w = dict(want)
    e = w["expect"]
    w["window"] = sorted([(a, b) for a, b in w["window"]], key=lambda kv: (kv[0] - e) % 16)
    w["events"] = [tuple(x) for x in w["events"]]
    return w


def _cmp(t):
    want = _norm_want(_ora_replay(t))
    try:
        raw = stateful.replay(t)
    except Exception:
        return False
    try:
        got = _norm(raw)
    except Exception:
        return False
    for k, v in want.items():
        if got[k] != v:
            return False
    return True


def _cmp_strict(t):
    """Compare strict-mode behaviour: same dict, or same (kind, index, events)."""
    try:
        want = _norm_want(_ora_replay(t, True))
        werr = None
    except _OraErr as e:
        want, werr = None, (e.kind, e.index, [tuple(x) for x in e.events])
    try:
        raw = stateful.replay(t, True)
        gerr = None
    except PE as e:
        raw = None
        k = getattr(e, "kind", None)
        ix = getattr(e, "index", None)
        evs = getattr(e, "events", None)
        if not isinstance(k, str) or isinstance(ix, bool) or not isinstance(ix, int):
            return False
        if not isinstance(evs, (list, tuple)):
            return False
        try:
            evs = [tuple(x) if isinstance(x, (list, tuple)) else _Bad() for x in evs]
        except Exception:
            return False
        if any(isinstance(x, _Bad) for x in evs):
            return False
        gerr = (k, ix, evs)
    except Exception:
        return False
    if werr is not None:
        return gerr == werr
    if gerr is not None:
        return False
    try:
        got = _norm(raw)
    except Exception:
        return False
    for k, v in want.items():
        if got[k] != v:
            return False
    return True


def _all(cases, fn=None):
    fn = fn or _cmp

    def probe():
        for c in cases:
            if not fn(c):
                return False
        return True
    return probe


def _slice(cases, k, i):
    return [c for j, c in enumerate(cases) if j % k == i]


def _kind_of(t):
    """(kind, index) reported by the candidate in strict mode, or a marker string."""
    try:
        stateful.replay(t, True)
    except PE as e:
        return (getattr(e, "kind", "<no .kind>"), getattr(e, "index", "<no .index>"))
    except Exception as e:
        return ("<%s>" % type(e).__name__, None)
    return ("<no raise>", None)


def _kinds(pairs):
    def probe():
        for t, want in pairs:
            if _kind_of(t) != want:
                return False
        return True
    return probe


# =====================================================================
# 1-2: bans
# =====================================================================
check("does not import struct/binascii/zlib/hashlib",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+(?:struct|binascii|zlib|hashlib)\b",
                            inspect.getsource(stateful), re.M))

check("does not import or call the time module",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+time\b",
                            inspect.getsource(stateful), re.M)
      and not re.search(r"\btime\s*\.\s*(?:time|monotonic|perf_counter|sleep)\b",
                        inspect.getsource(stateful)))

# =====================================================================
# 3-5: canonical output form
# =====================================================================
_H = F(1, 0, 0)


def form_probe():
    r = stateful.replay(_H + F(2, 1, 0, b"b") + F(2, 3, 0, b"d"))
    if not isinstance(r, dict) or set(r.keys()) != set(KEYS):
        return False
    if type(r["window"]) is not list or type(r["delivered"]) is not list:
        return False
    if type(r["events"]) is not list or type(r["state"]) is not str:
        return False
    if type(r["aborted"]) is not bool or type(r["clock"]) is not int:
        return False
    if type(r["expect"]) is not int or type(r["illegal"]) is not int:
        return False
    if type(r["frames"]) is not int or type(r["deadline"]) is not int:
        return False
    for it in r["window"]:
        if type(it) is not tuple or len(it) != 2:
            return False
        if type(it[0]) is not int or type(it[1]) is not bytes:
            return False
    r2 = stateful.replay(_H + F(2, 0, 0, b"a"))
    if r2["window"] != [] or [type(x) for x in r2["delivered"]] != [bytes]:
        return False
    if r2["delivered"] != [b"a"] or r2["aborted"] is not False:
        return False
    r3 = stateful.replay(b"")
    return (r3["events"] == [] and r3["state"] == "IDLE" and r3["deadline"] is None
            and r3["window"] == [] and r3["delivered"] == [] and r3["frames"] == 0
            and r3["aborted"] is False
            and stateful.replay(bytearray(_H))["state"] == "OPEN")


check("canonical form: exact key set and exact Python types", form_probe)


def window_probe():
    r = stateful.replay(F(1, 14, 0) + F(2, 1, 0, b"c") + F(2, 15, 0, b"a"))
    if r["expect"] != 14 or r["window"] != [(15, b"a"), (1, b"c")]:
        return False
    r = stateful.replay(F(1, 13, 0) + F(2, 0, 0, b"z") + F(2, 15, 0, b"y")
                        + F(2, 14, 0, b"x"))
    if r["expect"] != 13 or r["window"] != [(14, b"x"), (15, b"y"), (0, b"z")]:
        return False
    r = stateful.replay(F(1, 6, 0) + F(2, 9, 0, b"9") + F(2, 7, 0, b"7")
                        + F(2, 8, 0, b"8"))
    if r["window"] != [(7, b"7"), (8, b"8"), (9, b"9")]:
        return False
    r = stateful.replay(F(1, 15, 0) + F(2, 2, 0, b"2") + F(2, 0, 0, b"0"))
    return r["expect"] == 15 and r["window"] == [(0, b"0"), (2, b"2")]


check("canonical form: window is a list of tuples in ascending window order", window_probe)


def events_probe():
    r = stateful.replay(F(1, 14, 0) + F(2, 15, 0, b"a") + F(2, 15, 0, b"a2")
                        + F(2, 14, 0, b"x") + F(2, 6, 0, b"o") + F(4, 0, 0)
                        + F(5, 0, 0) + F(2, 0, 0, b"n"))
    want = [("hello", 0, 14), ("state", "OPEN"), ("buf", 1, 15), ("dup", 2, 15),
            ("deliver", 3, 14), ("flush", 15), ("drop", 4, "out_of_window"),
            ("close", 5), ("state", "DRAINING"), ("reset", 6), ("state", "IDLE"),
            ("illegal", 7, 2, "IDLE")]
    if r["events"] != want:
        return False
    if any(type(e) is not tuple for e in r["events"]):
        return False
    r = stateful.replay(b"\xaa" + F(1, 0, 0) + F(2, 1, 0, b"b") + F(3, 0, 21)
                        + F(5, 0, 0))
    want = [("junk", 1), ("hello", 0, 0), ("state", "OPEN"), ("buf", 1, 1),
            ("timeout", 21), ("state", "CLOSED"), ("discard", 1),
            ("illegal", 2, 3, "CLOSED"), ("reset", 3), ("state", "IDLE")]
    return r["events"] == want and all(type(e) is tuple for e in r["events"])


check("canonical form: event tuples, exact shapes and exact order", events_probe)


# =====================================================================
# 6: ProtocolError contract and argument rejection
# =====================================================================
def perr_probe():
    if PE is _MissingErr or not issubclass(PE, ValueError):
        return False
    for bad in ("abc", None, 12, [1, 2, 3], (1, 2), memoryview(b"\x7e"), 1.5,
                bytes, True):
        try:
            stateful.replay(bad)
        except PE as e:
            if getattr(e, "kind", None) != "bad_transcript":
                return False
            if getattr(e, "index", None) != -1 or list(getattr(e, "events", [1])) != []:
                return False
            continue
        except Exception:
            return False
        return False
    try:
        stateful.replay("abc", True)
    except PE as e:
        if getattr(e, "kind", None) != "bad_transcript":
            return False
    except Exception:
        return False
    # non-strict mode must never raise, however broken the stream
    for t in (b"", b"\x7e", b"\x7d", b"\x7e\x7d\x7e", b"\xff" * 5,
              F(2, 8, 0, b"x", ck=3), F(9, 0, 0, b"", ln=200)):
        try:
            if not isinstance(stateful.replay(t), dict):
                return False
        except Exception:
            return False
    # a transcript with no drop/illegal/timeout/abort event replays fine in strict mode
    ok = F(1, 0, 0) + F(2, 1, 0, b"b") + F(2, 0, 0, b"a") + F(4, 0, 0)
    return stateful.replay(ok, True) == stateful.replay(ok)


check("ProtocolError contract: subclasses ValueError, rejects non-bytes transcripts",
      perr_probe)

# =====================================================================
# 7-8: strict-mode error kinds
# =====================================================================
check("strict mode: framing error kinds and .index",
      _kinds([(F(1, 0, 0, b"a", ck=0), ("bad_checksum", 0)),
              (_H + F(2, 0, 0, b"a", ck=9), ("bad_checksum", 1)),
              (_H + F(2, 0, 0, b"a", ln=9), ("bad_length", 1)),
              (F(1, 0, 0, b"", ln=255), ("bad_length", 0)),
              (_H + F(2, 0, 0, b"abc")[:4], ("truncated", 1)),
              (b"\x7e", ("truncated", 0)),
              (b"\x7e\x7e", ("truncated", 0)),
              (_H + b"\x7e\x00\x02\x7d\x7e" + _H, ("bad_escape", 1)),
              (b"\xaa\xbb\x7e\x00\x02\x00\x7d\x7e", ("bad_escape", 0)),
              (_H + b"\x7e\x7d\x7e", ("bad_escape", 1)),
              (_H + F(9, 0, 0), ("bad_type", 1)),
              (_H + F(0, 0, 0), ("bad_type", 1)),
              (_H + F(200, 0, 0), ("bad_type", 1)),
              (_H + F(2, 0, 0, b"a"), ("<no raise>", None))]))

check("strict mode: state, sequence and timeout error kinds and .index",
      _kinds([(F(2, 0, 0, b"a"), ("illegal", 0)),
              (F(3, 0, 0), ("illegal", 0)),
              (F(4, 0, 0), ("illegal", 0)),
              (_H + F(1, 0, 0), ("illegal", 1)),
              (_H + F(2, 8, 0, b"x"), ("out_of_window", 1)),
              (_H + F(2, 4, 0, b"x"), ("out_of_window", 1)),
              (_H + F(2, 11, 0, b"x"), ("out_of_window", 1)),
              (_H + F(2, 12, 0, b"x"), ("<no raise>", None)),
              (_H + F(2, 3, 0, b"x"), ("<no raise>", None)),
              (_H + F(4, 0, 0) + F(2, 0, 0, b"a"), ("draining", 2)),
              (_H + F(4, 0, 0) + F(4, 0, 0) + F(3, 0, 0), ("illegal", 3)),
              (_H + F(3, 0, 21), ("timeout", -1)),
              (_H + F(2, 0, 20, b"a"), ("<no raise>", None)),
              (_H + F(2, 0, 21, b"a"), ("timeout", -1)),
              (F(5, 0, 0) + F(5, 0, 0) + _H, ("<no raise>", None))]))

# =====================================================================
# 9-11: precedence over multiply-invalid frames
# =====================================================================
_PREC = [
    # bad checksum AND out of window AND illegal in state
    F(2, 8, 0, b"x", ck=0),
    _H + F(2, 8, 0, b"x", ck=0),
    _H + F(4, 0, 0) + F(2, 8, 0, b"x", ck=0),
    # bad length AND unknown type AND illegal in state
    F(200, 9, 0, b"a", ln=9),
    _H + F(200, 9, 0, b"a", ln=9),
    # truncated AND unknown type AND illegal
    F(200, 9, 0, b"abc")[:4],
    _H + F(200, 9, 0, b"abc")[:4],
    # unknown type AND illegal in state (bad_type wins)
    F(9, 8, 0),
    _H + F(4, 0, 0) + F(9, 8, 0),
    _H + F(4, 0, 0) + F(4, 0, 0) + F(9, 8, 0),
    # timeout AND illegal / out of window / bad type in the same frame
    _H + F(1, 0, 21),
    _H + F(2, 8, 21, b"x"),
    _H + F(9, 0, 21),
    _H + F(2, 0, 21, b"a", ck=0),
    _H + F(2, 1, 0, b"b") + F(5, 0, 21),
    _H + F(2, 1, 0, b"b") + F(2, 8, 21, b"x"),
    # draining beats out_of_window and beats illegal
    _H + F(4, 0, 0) + F(2, 8, 0, b"x"),
    _H + F(4, 0, 0) + F(4, 0, 0) + F(2, 8, 0, b"x"),
    # illegal beats out_of_window (state checked before sequence)
    F(2, 8, 0, b"x") + F(2, 9, 0, b"y") + F(2, 10, 0, b"z") + F(1, 0, 0),
    # bad escape beats everything downstream
    _H + b"\x7e\x7d\x7e" + F(9, 8, 0),
]
for _i in range(2):
    check("precedence: frames that break several rules at once (bucket %d)" % (_i + 1),
          _all(_slice(_PREC, 2, _i), _cmp_strict))

# =====================================================================
# 12: visible examples
# =====================================================================
def visible_probe():
    r = _norm(stateful.replay(F(1, 0, 1) + F(2, 0, 2, b"ab") + F(2, 1, 2, b"c")
                              + F(4, 0, 1)))
    if r["events"] != [("hello", 0, 0), ("state", "OPEN"), ("deliver", 1, 0),
                       ("deliver", 2, 1), ("close", 3), ("state", "DRAINING")]:
        return False
    if (r["state"], r["clock"], r["expect"], r["deadline"], r["frames"]) != \
            ("DRAINING", 6, 2, 26, 4):
        return False
    if r["delivered"] != [b"ab", b"c"]:
        return False
    r = _norm(stateful.replay(F(1, 3, 0) + F(2, 4, 1, b"x") + F(2, 3, 1, b"w")))
    if r["events"] != [("hello", 0, 3), ("state", "OPEN"), ("buf", 1, 4),
                       ("deliver", 2, 3), ("flush", 4)]:
        return False
    if r["delivered"] != [b"w", b"x"] or r["expect"] != 5 or r["deadline"] != 22:
        return False
    r = _norm(stateful.replay(b"\x01\x02" + F(2, 0, 0, b"z", ck=0) + F(1, 0, 0)))
    if r["events"] != [("junk", 2), ("drop", 0, "bad_checksum"), ("hello", 1, 0),
                       ("state", "OPEN")]:
        return False
    if r["clock"] != 0 or r["frames"] != 2:
        return False
    r = _norm(stateful.replay(F(2, 0, 0, b"q") + F(9, 0, 0) + F(1, 0, 0)))
    return r["events"] == [("illegal", 0, 2, "IDLE"), ("drop", 1, "bad_type"),
                           ("hello", 2, 0), ("state", "OPEN")] and r["illegal"] == 1


check("the four documented examples are exactly reproduced", visible_probe)

# =====================================================================
# 13-14: crafted framing cases
# =====================================================================
_FRAMING = [
    b"",
    b"\x7e",
    b"\x00\x11\x22",
    b"\x7e\x7e\x7e",
    _H + b"\x7e" + F(2, 0, 0, b"a"),
    _H + b"\x7e\x00\x02\x00" + F(2, 0, 0, b"a"),
    _H + b"\x7e\x7d" + F(2, 0, 0, b"a"),
    _H + b"\x7e\x00\x02\x7d",
    _H + b"\x7e\x00\x02\x00\x7d",
    _H + F(2, 0, 0, b"a")[:-1],
    _H + F(2, 0, 0, b"abc")[:4],
    _H + F(2, 0, 0, b"a", ln=9) + F(2, 0, 0, b"b"),
    _H + F(2, 0, 0, b"a", ln=200) + F(2, 0, 0, b"b"),
    _H + F(2, 0, 0, b"a", ln=9) + b"\xaa\xbb" + F(2, 0, 0, b"b"),
    _H + F(2, 0, 0, b"a", ck=0) + F(2, 0, 0, b"b"),
    _H + F(2, 0, 0, b"a", ck=0) + b"\x01\x02\x03" + F(2, 0, 0, b"b"),
    _H + F(2, 0, 0, b"a") + b"\xff\xff",
    _H + F(2, 0, 0, b"\x7e\x7d") + F(2, 1, 0, b"\x7e"),
    _H + F(2, 0, 0x7e, b"") + F(2, 1, 0x7d, b""),
    _H + F(2, 0, 0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
    _H + F(2, 0, 0, b"", ck=0x7e),
    b"\x7d\x5e" + _H,
    b"\x7d" + _H,
    _H + b"\x7d\x5e\x00\x02\x00\x02",
    _H + F(2, 0, 0, b"a") + b"\x7d",
    F(1, 0, 0, b"", ln=8) + _H,
    _H + b"\x7e" * 5 + F(2, 0, 0, b"a"),
    _H + F(3, 0, 0)[:2] + F(2, 0, 0, b"a"),
]
for _i in range(2):
    check("framing: stray FLAG, escapes, bad length/checksum, resync (bucket %d)" % (_i + 1),
          _all(_slice(_FRAMING, 2, _i)))

# =====================================================================
# 15-16: crafted state-machine cases
# =====================================================================
_STATE = [
    F(2, 0, 0, b"a") + F(2, 0, 0, b"b") + F(2, 0, 0, b"c") + F(1, 0, 0),
    F(2, 0, 0, b"a") + F(2, 0, 0, b"b") + F(2, 0, 0, b"c") + b"\xaa\xbb",
    _H + F(1, 0, 0) + F(1, 0, 0),
    _H + F(2, 1, 0, b"x") + F(1, 0, 0) + F(1, 0, 0) + F(1, 0, 0) + F(3, 0, 0),
    _H + F(4, 0, 0) + F(4, 0, 0) + F(3, 0, 0),
    _H + F(4, 0, 0) + F(2, 0, 0, b"a") + F(3, 0, 0) + F(4, 0, 0) + F(2, 0, 0, b"b"),
    _H + F(2, 1, 0, b"x") + F(2, 2, 0, b"y") + F(4, 0, 0),
    _H + F(2, 1, 0, b"x") + F(2, 3, 0, b"z") + F(4, 0, 0) + F(2, 4, 0, b"q"),
    F(5, 0, 0) + F(5, 0, 0) + _H,
    _H + F(2, 1, 0, b"x") + F(2, 2, 0, b"y") + F(5, 0, 0) + F(1, 5, 0),
    _H + F(4, 0, 0) + F(5, 0, 0) + F(1, 2, 0) + F(2, 2, 0, b"m"),
    _H + F(4, 0, 0) + F(4, 0, 0) + F(5, 0, 0) + F(1, 0, 0) + F(2, 0, 0, b"n"),
    _H + F(3, 0, 0) + F(3, 0, 0) + F(2, 0, 0, b"a"),
    _H + F(2, 0, 0) + F(2, 1, 0) + F(4, 0, 0),
    F(4, 0, 0) + F(3, 0, 0) + F(1, 0, 0) + F(1, 0, 0),
    _H + F(2, 2, 0, b"p") + F(1, 0, 0) + F(1, 0, 0) + F(1, 0, 0) + F(5, 0, 0),
    _H + F(6, 0, 0) + F(0, 0, 0) + F(255, 0, 0) + F(2, 0, 0, b"a"),
    F(3, 0, 0) + F(4, 0, 0) + F(2, 0, 0) + F(1, 0, 0) + F(1, 0, 0),
]
for _i in range(2):
    check("state machine: legality table, abort, reset, close/drain (bucket %d)" % (_i + 1),
          _all(_slice(_STATE, 2, _i)))

# =====================================================================
# 17: crafted sequence / wraparound cases
# =====================================================================
_SEQ = [
    F(1, 14, 0) + F(2, 14, 0, b"a") + F(2, 15, 0, b"b") + F(2, 0, 0, b"c")
    + F(2, 1, 0, b"d"),
    F(1, 14, 0) + F(2, 15, 0, b"b") + F(2, 0, 0, b"c") + F(2, 1, 0, b"d")
    + F(2, 14, 0, b"a"),
    F(1, 0, 0) + F(2, 1, 0, b"1") + F(2, 2, 0, b"2") + F(2, 3, 0, b"3")
    + F(2, 0, 0, b"0"),
    F(1, 0, 0) + F(2, 3, 0, b"3") + F(2, 3, 0, b"3b") + F(2, 0, 0, b"0"),
    F(1, 0, 0) + F(2, 4, 0, b"x") + F(2, 5, 0, b"y") + F(2, 11, 0, b"z"),
    F(1, 0, 0) + F(2, 12, 0, b"x") + F(2, 15, 0, b"y") + F(2, 13, 0, b"z"),
    F(1, 0, 0) + F(2, 0, 0, b"a") + F(2, 0, 0, b"a2") + F(2, 15, 0, b"w"),
    F(1, 0, 0) + F(2, 0, 0, b"a") + F(2, 1, 0, b"b") + F(2, 0, 0, b"a2")
    + F(2, 1, 0, b"b2"),
    F(1, 200, 0) + F(2, 200, 0, b"a") + F(2, 201, 0, b"b"),
    F(1, 0, 0) + F(2, 16, 0, b"a") + F(2, 17, 0, b"b") + F(2, 32, 0, b"c"),
    F(1, 13, 0) + F(2, 14, 0, b"n") + F(2, 15, 0, b"o") + F(2, 0, 0, b"p")
    + F(2, 13, 0, b"m"),
    F(1, 0, 0) + F(2, 2, 0, b"c") + F(2, 1, 0, b"b") + F(2, 3, 0, b"d")
    + F(2, 0, 0, b"a"),
    F(1, 5, 0) + F(2, 6, 0, b"x") + F(2, 7, 0, b"y") + F(5, 0, 0) + F(1, 6, 0)
    + F(2, 6, 0, b"z"),
    F(1, 0, 0) + F(2, 0, 0) + F(2, 1, 0) + F(2, 2, 0) + F(2, 3, 0),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(2, 2, 0, b"c") + F(4, 0, 0) + F(4, 0, 0),
    F(1, 15, 0) + F(2, 1, 0, b"x") + F(2, 2, 0, b"y") + F(2, 15, 0, b"o")
    + F(2, 0, 0, b"z"),
    F(1, 0, 0) + F(2, 8, 0, b"h") + F(2, 4, 0, b"e") + F(2, 12, 0, b"l")
    + F(2, 0, 0, b"a"),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(5, 0, 0) + F(2, 1, 0, b"b2") + F(1, 1, 0)
    + F(2, 1, 0, b"b3"),
    F(1, 14, 0) + F(2, 1, 0, b"c") + F(2, 15, 0, b"a") + F(4, 0, 0),
    F(1, 14, 0) + F(2, 1, 0, b"c") + F(2, 0, 0, b"b") + F(2, 15, 0, b"a")
    + F(5, 0, 0) + F(1, 0, 0),
    F(1, 12, 0) + F(2, 15, 0, b"z") + F(2, 13, 0, b"y") + F(3, 0, 21) + F(1, 0, 0),
]
check("sequence: wraparound, dup, window bounds, flush chain (crafted)", _all(_SEQ))

# =====================================================================
# 18: crafted timeout cases
# =====================================================================
_TIME = [
    F(1, 0, 0) + F(2, 0, 20, b"a"),
    F(1, 0, 0) + F(2, 0, 21, b"a"),
    F(1, 0, 0) + F(3, 0, 21) + F(5, 0, 0) + F(1, 0, 0),
    F(1, 0, 5) + F(3, 0, 20) + F(3, 0, 20) + F(3, 0, 1),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(2, 5, 21, b"x") + F(2, 0, 0, b"a"),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(3, 0, 21) + F(3, 0, 0),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(2, 1, 25, b"b2") + F(2, 0, 0, b"a"),
    F(1, 0, 0) + F(9, 0, 21) + F(2, 0, 0, b"a"),
    F(1, 0, 0) + F(2, 0, 0, b"a", ck=1) + F(2, 0, 21, b"b"),
    F(1, 0, 0) + F(2, 0, 0, b"a", ck=1) + F(2, 0, 20, b"b"),
    F(1, 0, 0) + F(2, 4, 21, b"x") + F(2, 0, 0, b"a"),
    F(1, 0, 0) + F(2, 1, 10, b"b") + F(2, 2, 10, b"c") + F(2, 0, 1, b"a"),
    F(1, 0, 0) + F(2, 1, 10, b"b") + F(2, 2, 11, b"c") + F(2, 0, 1, b"a"),
    F(1, 0, 63) + F(2, 0, 63, b"a") + F(3, 0, 63),
    F(1, 0, 0) + F(4, 0, 21) + F(1, 0, 0),
    F(1, 0, 0) + F(4, 0, 5) + F(2, 0, 21, b"a") + F(3, 0, 0),
    F(1, 0, 0) + F(3, 0, 84) + F(3, 0, 0),
    F(1, 0, 0) + F(2, 1, 0, b"b") + F(2, 12, 21, b"o") + F(3, 0, 0),
]
check("timeouts: strict boundary, fires before processing, timer resets (crafted)",
      _all(_TIME))


# =====================================================================
# randomised transcript generation
# =====================================================================
def _corrupt(rng, wire):
    w = bytearray(wire)
    r = rng.random()
    if r < 0.25 and len(w) > 2:
        w[rng.randrange(1, len(w))] ^= 1 << rng.randrange(8)
    elif r < 0.45 and len(w) > 2:
        del w[rng.randrange(1, len(w)):]
    elif r < 0.60:
        w += bytes([rng.choice([0x00, 0xAA, 0xFF, 0x7D, 0x01])
                    for _ in range(rng.randint(1, 3))])
    elif r < 0.72:
        w.insert(rng.randrange(1, len(w) + 1), FLAG)
    elif r < 0.84:
        p = rng.randrange(1, len(w) + 1)
        w[p:p] = bytes([ESC, FLAG])
    else:
        w = bytearray([FLAG]) + w[1:]
    return bytes(w)


def _gen(rng, mode):
    out = bytearray()
    nf = rng.randint(2, 14)
    seqbase = rng.randrange(16)
    for _ in range(nf):
        if mode == "seq":
            ty = rng.choice([2, 2, 2, 2, 1, 4, 5, 3])
            seq = (seqbase + rng.choice([0, 1, 2, 3, 4, 5, 8, 11, 12, 15, 16, 200])) % 256
            tick = rng.choice([0, 0, 1, 2])
        elif mode == "time":
            ty = rng.choice([2, 2, 3, 1, 4, 5])
            seq = (seqbase + rng.choice([0, 1, 2, 4, 12, 15])) % 16
            tick = rng.choice([0, 1, 5, 10, 19, 20, 21, 25])
        elif mode == "frame":
            ty = rng.choice([1, 2, 2, 3, 4, 5, 0, 6, 9, 200])
            seq = rng.randrange(256)
            tick = rng.choice([0, 1, 2, 0x7E, 0x7D])
        else:
            ty = rng.choice([1, 2, 2, 2, 3, 4, 5, 7])
            seq = (seqbase + rng.choice([0, 1, 2, 3, 5, 12, 15, 40])) % 256
            tick = rng.choice([0, 1, 3, 10, 20, 21])
        plen = rng.choice([0, 0, 1, 1, 2, 3])
        pay = bytes([rng.choice([0x41, 0x42, 0x00, 0x7E, 0x7D, 0xFF])
                     for _ in range(plen)])
        ln = None
        ck = None
        if mode in ("frame", "mixed") and rng.random() < 0.10:
            ln = rng.choice([9, 20, 255])
        if mode in ("frame", "mixed") and rng.random() < 0.10:
            ck = rng.randrange(256)
        wire = F(ty, seq, tick, pay, ln=ln, ck=ck)
        if mode == "frame" and rng.random() < 0.45:
            wire = _corrupt(rng, wire)
        elif mode == "mixed" and rng.random() < 0.18:
            wire = _corrupt(rng, wire)
        if rng.random() < (0.30 if mode in ("frame", "mixed") else 0.06):
            out += bytes([rng.choice([0x00, 0x33, 0xFF, 0x7D])
                          for _ in range(rng.randint(1, 3))])
        out += wire
        if rng.random() < 0.05:
            seqbase = rng.randrange(16)
    return bytes(out[:400])


def gen_cases(seed, n, mode):
    rng = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 60:
        tries += 1
        t = _gen(rng, mode)
        if mode == "time":
            evs = _ora_replay(t)["events"]
            if not any(e[0] == "timeout" for e in evs) and rng.random() < 0.85:
                continue
        out.append(t)
    while len(out) < n:
        out.append(_gen(rng, mode))
    return out


# =====================================================================
# 19: randomised precedence probe (strict mode over corrupt traffic)
# =====================================================================
_RF = gen_cases(5701, 900, "frame")
check("precedence: randomised differential in strict mode",
      _all(_slice(_RF, 4, 0), _cmp_strict))

# =====================================================================
# 20-21: randomised corrupt framing
# =====================================================================
for _i in range(2):
    check("randomised differential, corrupt framing (bucket %d)" % (_i + 1),
          _all(_slice(_RF, 2, _i)))

# =====================================================================
# 22-23: randomised sequence / wraparound traffic
# =====================================================================
_RS = gen_cases(5702, 900, "seq")
for _i in range(2):
    check("randomised differential, sequence/wraparound traffic (bucket %d)" % (_i + 1),
          _all(_slice(_RS, 2, _i)))

# =====================================================================
# 24-25: randomised timeout-heavy traffic
# =====================================================================
_RT = gen_cases(5703, 600, "time")
for _i in range(2):
    check("randomised differential, timeout-heavy traffic (bucket %d)" % (_i + 1),
          _all(_slice(_RT, 2, _i)))

# =====================================================================
# 26: everything mixed
# =====================================================================
_RM = gen_cases(5704, 900, "mixed")
check("randomised differential, everything mixed", _all(_RM))

check("randomised differential, everything mixed in strict mode",
      _all(_slice(_RM, 3, 0), _cmp_strict))

_t.cancel()
report()
