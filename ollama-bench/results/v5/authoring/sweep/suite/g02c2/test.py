import hashlib
import os
import sys
import threading

TOTAL = 12
fails = []
done = 0
runtime_bad = False
_lock = threading.Lock()
_TEST_SHA256 = "95c4920b4dac701f71370acb2740292e877917d0f6f90688511bdd08f3d24e43"
# Hash the pristine implementation so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "imports.py": "559e108b511990df2789b81a08a09ff0d945d8c57ae182a8fd3646086038dcb4",
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


def check(name, fn):
    global done, runtime_bad
    try:
        ok = bool(fn())
    except Exception as exc:
        ok = False
        runtime_bad = True
        name = "%s raised %s" % (name, type(exc).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def report():
    timer.cancel()
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if not fails:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL", fails[:10])
    print("VERDICT", "visibly_failed" if runtime_bad or not _candidate_worked()
          else "confidently_wrong")
    sys.exit(1)


timer = threading.Timer(45.0, _watchdog)
timer.daemon = True
timer.start()
try:
    import imports as _candidate
except Exception as exc:
    runtime_bad = True
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    report()


def _ora_hash_test():
    with open("test_imports.py", "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest() == _TEST_SHA256


def _ora_expected(source, old, new):
    """A deliberately tiny oracle for exact module-name replacement."""
    return source.replace("from " + old, "from " + new).replace("import " + old, "import " + new)


check("test file is unchanged", _ora_hash_test)
check("plain import", lambda: _candidate.rewrite_source("import oldpkg.tools as tools\n", {"oldpkg": "newpkg"}) == "import newpkg.tools as tools\n")
check("from import", lambda: _candidate.rewrite_source("from oldpkg.widgets import Button\n", {"oldpkg": "newpkg"}) == "from newpkg.widgets import Button\n")
check("multiline from import", lambda: _candidate.rewrite_source("from oldpkg.sub import (\n    A, B,\n)\n", {"oldpkg": "newpkg"}) == "from newpkg.sub import (\n    A, B,\n)\n")
check("comments and strings", lambda: _candidate.rewrite_source('# import oldpkg\nvalue = "import oldpkg"\nimport oldpkg\n', {"oldpkg": "newpkg"}) == '# import oldpkg\nvalue = "import oldpkg"\nimport newpkg\n')
check("prefix boundary", lambda: _candidate.rewrite_source("import oldpkgx\nimport oldpkg.extra\n", {"oldpkg": "newpkg"}) == "import oldpkgx\nimport newpkg.extra\n")
check("multiple imports", lambda: _candidate.rewrite_source("import oldpkg.a, other, oldpkg.b\n", {"oldpkg": "newpkg"}) == "import newpkg.a, other, newpkg.b\n")
check("relative untouched", lambda: _candidate.rewrite_source("from .oldpkg import value\n", {"oldpkg": "newpkg"}) == "from .oldpkg import value\n")
check("module listing", lambda: _candidate.imported_modules("import one.two\nimport three, four.five\n") == ["one.two", "three", "four.five"])
check("changed positive", lambda: _candidate.changed("from oldpkg import X\n", {"oldpkg": "newpkg"}) is True)
check("changed negative", lambda: _candidate.changed("from other import X\n", {"oldpkg": "newpkg"}) is False)
check("rewrite many", lambda: _candidate.rewrite_many(["import oldpkg.a\n", "import other\n"], {"oldpkg": "newpkg"}) == ["import newpkg.a\n", "import other\n"])
report()
