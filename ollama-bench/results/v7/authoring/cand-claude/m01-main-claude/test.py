import os
import sys
import threading

_ora_total = 12
_ora_done = 0
_ora_fails = []
_ora_lock = threading.Lock()
_ora_shape = False
_ora_verdict_override = None


def _ora_check(name, fn):
    global _ora_done
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _ora_fails.append(name)
    with _ora_lock:
        _ora_done += 1


def _ora_watchdog():
    with _ora_lock:
        n = max(0, min(_ora_total, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (n, _ora_total))
    print("FAIL ['grader timed out']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_report():
    _ora_timer.cancel()
    # clamped: a verdict override may append a reason beyond the subcheck count, and a
    # negative score is a grader artifact rather than a result.
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %d/%d" % (n, _ora_total))
    if _ora_verdict_override:
        if not _ora_fails:
            print("FAIL []")
        else:
            print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        sys.exit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    sys.exit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()

import importlib
import inspect

PKG = 'cinder'
MODULE = 'dispatch_gate'
CLS = 'DispatchLedger'
WINDOW = 60

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

_eng = None
_mut = None
try:
    _mod = importlib.import_module(PKG + "." + MODULE)
    _cls = getattr(_mod, CLS)
    _mut = [n for n, f in inspect.getmembers(_cls, inspect.isfunction)
            if not n.startswith("_") and list(inspect.signature(f).parameters) ==
            ["self", "key", "payload"]]
    _eng = _cls(limit=1000, window_s=WINDOW)
    _ora_shape = (hasattr(_eng, "reap") and hasattr(_eng, "active_count")
                  and callable(_eng.reap) and callable(_eng.active_count))
except Exception:
    _eng = None
    _ora_shape = False


def _fresh():
    e = _cls(limit=1000, window_s=WINDOW)
    add = getattr(e, sorted(_mut)[0])
    for k in ("a", "b", "c", "d"):
        add(k)
    return e, add


def _state(engine, key):
    for rec in engine.snapshot():
        if rec["key"] == key:
            return rec["state"]
    return None


_ages = {"a": WINDOW + 1, "b": WINDOW * 10, "c": WINDOW, "d": 0}


def _reaped_count():
    e, _ = _fresh()
    return e.reap(dict(_ages))


def _after():
    e, _ = _fresh()
    e.reap(dict(_ages))
    return e


if _ora_shape:
    _ora_check("reap returns an int", lambda: type(_reaped_count()) is int)
    _ora_check("reap counts only records past the window",
               lambda: _reaped_count() == 2)
    _ora_check("a reaped record is still in the snapshot",
               lambda: len(_after().snapshot()) == 4)
    _ora_check("no record is removed from the stage",
               lambda: sorted(r["key"] for r in _after().snapshot()) == ["a", "b", "c", "d"])
    _ora_check("a reaped record's state is abandoned",
               lambda: _state(_after(), "a") == "abandoned")
    _ora_check("a second reaped record's state is abandoned",
               lambda: _state(_after(), "b") == "abandoned")
    _ora_check("a record exactly at the window is not reaped",
               lambda: _state(_after(), "c") != "abandoned")
    _ora_check("a young record is not reaped",
               lambda: _state(_after(), "d") != "abandoned")
    _ora_check("active_count returns an int",
               lambda: type(_after().active_count()) is int)
    _ora_check("abandoned records stop counting against the limit",
               lambda: _after().active_count() == 2)
    _ora_check("active_count before any reaping counts every record",
               lambda: _fresh()[0].active_count() == 4)

    def _idempotent():
        e, _ = _fresh()
        e.reap(dict(_ages))
        return e.reap(dict(_ages)) == 0
    _ora_check("reaping twice reaps nothing the second time", _idempotent)
else:
    for _n in range(12):
        _ora_check("module did not import with reap and active_count", lambda: False)

_ora_report()
