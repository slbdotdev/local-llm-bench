import hashlib
import os
import sys
import threading


TOTAL = 13
fails = []
done = 0
runtime_bad = False
lock = threading.Lock()
_TEST_SHA256 = "3a4df76ec82d8a788b7783972c95164033043e4df0a3976ff02e7d831dc304c2"
_SEED_SHA256 = {
    "calls.py": "4b569670cc3187a444c314eb52b5f55e1ac77ca3a1d2240443780fd4b8537c30",
}


def _ora_candidate_worked():
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
    with lock:
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
    print("VERDICT", "visibly_failed" if runtime_bad or not _ora_candidate_worked()
          else "confidently_wrong")
    sys.exit(1)


timer = threading.Timer(45.0, _watchdog)
timer.daemon = True
timer.start()
try:
    import calls as _candidate
except Exception as exc:
    runtime_bad = True
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    report()


def _ora_hash_test():
    with open("test_calls.py", "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest() == _TEST_SHA256


check("test file is unchanged", _ora_hash_test)
check("exact call targets", lambda: _candidate.rewrite_calls(
    "oldpkg.run(1)\nresult = oldpkg.run (2)\nother(oldpkg.run(3), oldpkg.stop())\n",
    {"oldpkg.run": "newpkg.call"}) ==
    "newpkg.call(1)\nresult = newpkg.call (2)\nother(newpkg.call(3), oldpkg.stop())\n")
check("attribute and string protection", lambda: _candidate.rewrite_calls(
    "value = oldpkg.run\ntext = 'oldpkg.run()'\n",
    {"oldpkg.run": "newpkg.call"}) ==
    "value = oldpkg.run\ntext = 'oldpkg.run()'\n")
check("maximal exact match", lambda: _candidate.rewrite_calls(
    "oldpkg.runner()\noldpkg.run.extra()\nobj.oldpkg.run()\n",
    {"oldpkg.run": "newpkg.call"}) ==
    "oldpkg.runner()\noldpkg.run.extra()\nobj.oldpkg.run()\n")
check("comments and layout", lambda: _candidate.rewrite_calls(
    "# oldpkg.run()\noldpkg.run(4)  # oldpkg.run()\n",
    {"oldpkg.run": "newpkg.call"}) ==
    "# oldpkg.run()\nnewpkg.call(4)  # oldpkg.run()\n")
check("newline boundary", lambda: _candidate.rewrite_calls(
    "oldpkg.run\n()\n", {"oldpkg.run": "newpkg.call"}) == "oldpkg.run\n()\n")
check("definitions are not calls", lambda: _candidate.rewrite_calls(
    "def oldpkg():\n    return 1\nclass oldpkg():\n    pass\n",
    {"oldpkg": "newpkg"}) ==
    "def oldpkg():\n    return 1\nclass oldpkg():\n    pass\n")
check("nested call order", lambda: _candidate.called_names(
    "outer(oldpkg.run(), obj.done())\noldpkg.stop()\n") ==
    ["outer", "oldpkg.run", "obj.done", "oldpkg.stop"])
check("all call count", lambda: _candidate.call_count(
    "oldpkg.run()\noldpkg.runner()\noldpkg.run()\n") == 3)
check("exact call count", lambda: _candidate.call_count(
    "oldpkg.run()\noldpkg.runner()\noldpkg.run()\n", "oldpkg.run") == 2)
check("batch rewrite", lambda: _candidate.rewrite_many(
    ["oldpkg.run()\n", "other()\n"], {"oldpkg.run": "newpkg.call"}) ==
    ["newpkg.call()\n", "other()\n"])
check("changed positive", lambda: _candidate.changed(
    "oldpkg.run()\n", {"oldpkg.run": "newpkg.call"}) is True)
check("changed negative", lambda: _candidate.changed(
    "oldpkg.runner()\n", {"oldpkg.run": "newpkg.call"}) is False)
report()
