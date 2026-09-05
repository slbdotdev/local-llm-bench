import hashlib
import os
import sys
import threading


INITIAL_SCHEMA_SHA256 = "1fb8425f0158f0f1fc3a4ac763e2df49e5d6eff8bb5f8a2567ab16d81c63c2f9"
_ora_total = 6
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
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %d/%d" % (n, _ora_total))
    if _ora_verdict_override:
        print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        raise SystemExit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        raise SystemExit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    raise SystemExit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def main():
    global _ora_shape
    root = os.getcwd()
    source = os.path.join(root, "src", "harbor", "schema_store.py")
    source_text = read_text(source)
    _ora_shape = hashlib.sha256(source_text.encode("utf-8")).hexdigest() != INITIAL_SCHEMA_SHA256
    sys.path.insert(0, os.path.join(root, "src"))
    try:
        from harbor.schema_store import SchemaPlanner
        from harbor.envelope_view import EnvelopeRegistry
        schema = SchemaPlanner()
        for key in ("m", "z", "a"):
            schema.classify(key)
        other = EnvelopeRegistry()
        for key in ("m", "z", "a"):
            other.advance(key)
        published = getattr(schema, "published_snapshot", None)
        _ora_shape = callable(published)
    except Exception:
        _ora_shape = False
        for number in range(_ora_total):
            _ora_check("schema behavior %d" % (number + 1), lambda: False)
        _ora_report()

    _ora_check("published_snapshot is callable", lambda: callable(published))
    _ora_check("published snapshot is descending",
               lambda: [row["key"] for row in schema.published_snapshot()] == ["z", "m", "a"])
    _ora_check("published snapshot contains all records",
               lambda: len(schema.published_snapshot()) == 3)
    _ora_check("schema snapshot remains ascending",
               lambda: [row["key"] for row in schema.snapshot()] == ["a", "m", "z"])
    _ora_check("unrelated stage snapshot remains ascending",
               lambda: [row["key"] for row in other.snapshot()] == ["a", "m", "z"])
    _ora_check("published ordering does not reverse schema ordering",
               lambda: [row["key"] for row in schema.snapshot()] == ["a", "m", "z"])
    _ora_report()


try:
    main()
except SystemExit:
    raise
except Exception:
    while _ora_done < _ora_total:
        _ora_check("grader setup", lambda: False)
    _ora_report()
