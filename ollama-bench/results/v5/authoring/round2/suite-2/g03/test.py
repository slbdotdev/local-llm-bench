import doctest
import hashlib
import inspect
import os
import sys
import threading

TOTAL = 15
_done = 0
_fails = []
_lock = threading.Lock()
_import_ok = False

# Hash only application files so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "event_core.py": "ef94743456cd200cc722991aa3cc92e2fca1ae9cf72f780a183d9880095084e3",
    "event_bus.py": "bb3795a293ed0dacd0154f5c7f73491b865874855d3b35fc35708fd8f7cae89c",
    "event_view.py": "7ece9529b68cd9c6e22399bb425a785626c734659f35c90a3bfbb690c22259f9",
}


def _candidate_worked():
    for path, expected in _SEED_SHA256.items():
        try:
            with open(path, "rb") as handle:
                data = handle.read()
        except OSError:
            return True
        normalised = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if hashlib.sha256(normalised).hexdigest() != expected:
            return True
    return False


def _check(name, fn):
    global _done
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _fails.append(name)
    with _lock:
        _done += 1


def _watchdog():
    n = max(0, min(TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _watchdog)
_timer.daemon = True
_timer.start()
sys.path.insert(0, os.getcwd())

try:
    import event_core as _core
    import event_bus as _bus
    import event_view as _view
    _import_ok = True
except Exception:
    _fails.extend(["import"] + ["not run"] * (TOTAL - 1))


def _source_clean():
    for name in ("event_core.py", "event_bus.py", "event_view.py"):
        with open(os.path.join(os.getcwd(), name), "r", encoding="utf-8") as fh:
            if "emit_event" in fh.read():
                return False
    return True


def _signature():
    params = inspect.signature(_core.publish_event).parameters
    return (list(params) == ["payload", "kind", "channel", "stamped"] and
            params["channel"].kind is inspect.Parameter.KEYWORD_ONLY and
            params["stamped"].kind is inspect.Parameter.KEYWORD_ONLY and
            params["channel"].default == "main" and
            params["stamped"].default is False)


def _positional_rejected():
    try:
        _core.publish_event("payload", "kind", "ops")
    except TypeError:
        return True
    return False


if _import_ok:
    _check("new symbol", lambda: callable(_core.publish_event))
    _check("old name absent", _source_clean)
    _check("exact signature", _signature)
    _check("argument order", lambda: _core.publish_event("payload", "kind", channel="ops") == "ops|kind|payload")
    _check("stamped output", lambda: _core.publish_event("payload", "kind", channel="ops", stamped=True) == "STAMP ops|kind|payload")
    _check("options keyword-only", _positional_rejected)
    _check("batch default", lambda: _core.batch([("a", "one"), ("b", "two")]) == ["main|a|one", "main|b|two"])
    _check("batch argument swap", lambda: _core.batch([("a", "one"), ("b", "two")], channel="ops") == ["ops|a|one", "ops|b|two"])
    _check("batch stamped propagation", lambda: _core.batch([("a", "one"), ("b", "two")], channel="ops", stamped=True) == ["STAMP ops|a|one", "STAMP ops|b|two"])
    _check("bus propagation", lambda: _bus.forward("kind", "payload", channel="bus", stamped=True) == "STAMP bus|kind|payload")
    _check("reflection order", lambda: _view.reflected(("kind", "payload"), channel="view") == "view|kind|payload")
    _check("reflection stamped", lambda: _view.reflected(("kind", "payload"), channel="view", stamped=True) == "STAMP view|kind|payload")
    _check("doctest", lambda: doctest.testmod(_core, verbose=False).failed == 0)
    _check("view default", lambda: _view.present("kind", "payload") == "main|kind|payload")
    _check("no extra-file dependence", lambda: _core.publish_event("p", "k") == "main|k|p")

n = max(0, min(TOTAL, TOTAL - len(_fails)))
print("SCORE %d/%d" % (n, TOTAL))
if n == TOTAL:
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)
print("FAIL", _fails[:10])
print("VERDICT %s" % ("confidently_wrong"
                      if _import_ok and _candidate_worked()
                      else "visibly_failed"))
sys.exit(1)
