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
    "stitch_base.py": "24baeaf2625eb2a526bfe1a89506e4e31a3f0ed6b306dbe66b1f5a742437f247",
    "stitch_ops.py": "1d096d1a3fb1faedddbf4e82c1470b4401e74fec7a50eda03685e74e8cae6041",
    "stitch_view.py": "e453665abbf2587230e023310895b164a30fc2ffa7dfdb3db74ec59f5d8d9bb5",
    "test_stitch.py": "a4cd5e686cf935d145cfc4a1650899792282c29b7d2960c8bbc5c23f6366a266",
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
    import stitch_base as _base
    import stitch_ops as _ops
    import stitch_view as _view
    _import_ok = True
except Exception:
    _fails.extend(["import"] + ["not run"] * (TOTAL - 1))


def _source_clean():
    for name in ("stitch_base.py", "stitch_ops.py", "stitch_view.py"):
        with open(os.path.join(os.getcwd(), name), "r", encoding="utf-8") as fh:
            if "join_bits" in fh.read():
                return False
    return True


if _import_ok:
    _check("new symbol", lambda: callable(_base.merge_bits))
    _check("old name absent", _source_clean)

    def _sig():
        p = inspect.signature(_base.merge_bits).parameters
        return (list(p) == ["right", "left", "glue"] and
                p["glue"].kind is inspect.Parameter.KEYWORD_ONLY and
                p["glue"].default == "-")

    _check("swapped signature", _sig)
    _check("swapped direct output", lambda: _base.merge_bits("R", "L", glue=":") == "[L:R]")

    def _positional_rejected():
        try:
            _base.merge_bits("R", "L", ":")
        except TypeError:
            return True
        return False

    _check("glue keyword-only", _positional_rejected)
    _check("row default", lambda: _base.make_row([("a", "b")]) == ["[a-b]"])
    _check("row comprehension order", lambda: _base.make_row([("a", "b"), ("c", "d")], glue=":") == ["[a:b]", "[c:d]"])
    _check("ops chain", lambda: _ops.decorate("a", "b", glue="/") == "[a/b]")
    _check("reflection order", lambda: _view.reflected(("x", "y"), glue="/") == "[y/x]")
    _check("doctest", lambda: doctest.testmod(_base, verbose=False).failed == 0)
    _check("view direct", lambda: _view.add_frame("u", "v") == "[u-v]")
    _check("no extra-file dependence", lambda: _base.merge_bits("b", "a") == "[a-b]")

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
