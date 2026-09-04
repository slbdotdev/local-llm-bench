import doctest
import hashlib
import inspect
import os
import sys
import threading

TOTAL = 12
_done = 0
_fails = []
_lock = threading.Lock()
_import_ok = False
# Hash pristine task files so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "badge_core.py": "e0d9fc623e250c25b5fdea6dceedf9fc651218d617f18a3f145008cb410f6f33",
    "badge_flow.py": "ae70a30b63b6117a0a44b408f50386afa089953796bcbfd8f5741579a65fb94f",
    "badge_registry.py": "f09c9ffc1e528350a9bd50eddae1880cc07fdf0ecf5a2e2bb3773599fd3114f0",
    "test_badges.py": "1754affd6a5222fa2d3615bd07b48f07287c501f182989d15eb9bee23b8d5528",
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
    import badge_core as _core
    import badge_flow as _flow
    import badge_registry as _registry
    _import_ok = True
except Exception:
    _fails.extend(["import"] + ["not run"] * (TOTAL - 1))


def _source_clean():
    root = os.getcwd()
    for name in ("badge_core.py", "badge_flow.py", "badge_registry.py"):
        with open(os.path.join(root, name), "r", encoding="utf-8") as fh:
            if "make_tag" in fh.read():
                return False
    return True


if _import_ok:
    _check("new symbol", lambda: callable(_core.make_badge))
    _check("old name absent", _source_clean)

    def _sig():
        p = inspect.signature(_core.make_badge).parameters
        return (list(p) == ["label", "tone"] and
                p["tone"].kind is inspect.Parameter.KEYWORD_ONLY and
                p["tone"].default == "plain")

    _check("keyword-only signature", _sig)
    _check("direct output", lambda: _core.make_badge("Ada", tone="warm") == "Ada<warm>")

    def _positional_rejected():
        try:
            _core.make_badge("Ada", "warm")
        except TypeError:
            return True
        return False

    _check("old positional call rejected", _positional_rejected)
    _check("default builder", lambda: _core.batch(["A"], tone="blue") == ["A<blue>"])
    _check("comprehension result", lambda: _core.batch(["A", "B"], tone="green") == ["A<green>", "B<green>"])
    _check("flow import", lambda: _flow.decorate("Q", tone="red") == "Q<red>")
    _check("reflection result", lambda: _registry.reflect("R", tone="gold") == "R<gold>")
    _check("registry chain", lambda: _registry.add_marker("S", tone="silver") == "S<silver>")
    _check("doctest", lambda: doctest.testmod(_core, verbose=False).failed == 0)
    _check("no extra-file dependence", lambda: _core.make_badge("Z") == "Z<plain>")

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
