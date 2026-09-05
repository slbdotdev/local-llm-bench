import doctest
import hashlib
import inspect
import os
import sys
import threading

TOTAL = 13
_done = 0
_fails = []
_lock = threading.Lock()
_import_ok = False
# Hash pristine task files so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "note_core.py": "2f5f5ee863c56a7ff588ed0bca8d7ca0e963e918b1b77969e789b1abfeabb473",
    "note_bus.py": "00e0b82adec270a79eb2f4b2c4ef908d730d7d72873f6100c2f9a7a71ffa4fc9",
    "note_view.py": "ae6c39c576d348cd4e949846232fdabeadfddc59b0df3f5b44fe27852f07f347",
    "test_notes.py": "b1927ca21b7a6fc6bf7030888a815b0aa95efeb02a84fea11e9a0f00cb17b064",
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
    import note_core as _core
    import note_bus as _bus
    import note_view as _view
    _import_ok = True
except Exception:
    _fails.extend(["import"] + ["not run"] * (TOTAL - 1))


def _source_clean():
    for name in ("note_core.py", "note_bus.py", "note_view.py"):
        with open(os.path.join(os.getcwd(), name), "r", encoding="utf-8") as fh:
            if "emit_note" in fh.read():
                return False
    return True


if _import_ok:
    _check("new symbol", lambda: callable(_core.write_note))
    _check("old name absent", _source_clean)

    def _sig():
        p = inspect.signature(_core.write_note).parameters
        return (list(p) == ["message", "channel", "urgent"] and
                p["channel"].kind is inspect.Parameter.KEYWORD_ONLY and
                p["urgent"].kind is inspect.Parameter.KEYWORD_ONLY and
                p["channel"].default == "log" and p["urgent"].default is False)

    _check("added option signature", _sig)
    _check("normal output", lambda: _core.write_note("hello", channel="chat") == "chat:hello")
    _check("urgent output", lambda: _core.write_note("hello", channel="chat", urgent=True) == "URGENT chat:hello")

    def _positional_rejected():
        try:
            _core.write_note("hello", "chat")
        except TypeError:
            return True
        return False

    _check("channel keyword-only", _positional_rejected)
    _check("bundle default", lambda: _core.bundle(["a", "b"], channel="inbox") == ["inbox:a", "inbox:b"])
    _check("bundle urgent propagation", lambda: _core.bundle(["a", "b"], channel="inbox", urgent=True) == ["URGENT inbox:a", "URGENT inbox:b"])
    _check("bus propagation", lambda: _bus.forward("x", channel="audit", urgent=True) == "URGENT audit:x")
    _check("reflection propagation", lambda: _view.reflected("x", channel="audit", urgent=True) == "URGENT audit:x")
    _check("doctest", lambda: doctest.testmod(_core, verbose=False).failed == 0)
    _check("view default", lambda: _view.present("x") == "log:x")
    _check("no extra-file dependence", lambda: _core.write_note("x") == "log:x")

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
