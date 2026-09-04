import hashlib
import os
import sys
import threading

TOTAL = 12
fails = []
done = 0
runtime_bad = False
_lock = threading.Lock()
_TEST_SHA256 = "3a4980742a22adfae34f7deae88abdb37e611c475a992405b17b472932f69c3d"
# Hash the pristine implementation so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "manifest_migrate.py": "fde445317dd716a493dbabd28eedbb71d9a2e278846ac2001899f0c68053584f",
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
    import manifest_migrate as _candidate
except Exception as exc:
    runtime_bad = True
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    report()


def _ora_hash_test():
    with open("test_manifest_migrate.py", "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest() == _TEST_SHA256


def _ora_migrate(text, mapping):
    lines = text.splitlines(True)
    result = []
    for line in lines:
        if line.rstrip("\r\n") == "# FROZEN BELOW":
            result.extend(lines[len(result):])
            break
        raw = line.rstrip("\r\n")
        ending = line[len(raw):]
        if ":" in raw and not raw.lstrip().startswith("#"):
            left, right = raw.split(":", 1)
            key = left.strip()
            if key in mapping and key and key.replace("_", "a").replace("-", "a").replace(".", "a").isalnum():
                lead = left[:len(left) - len(left.lstrip())]
                result.append(lead + mapping[key] + right[:0] + ":" + right + ending)
                continue
        result.append(line)
    else:
        return "".join(result)
    return "".join(result)


check("test file is unchanged", _ora_hash_test)
check("frozen suffix", lambda: _candidate.migrate("title: old\n# FROZEN BELOW\nold: keep\n", {"title": "new", "old": "new"}) == "new: old\n# FROZEN BELOW\nold: keep\n")
check("editable keys", lambda: _candidate.migrate("old: one\nother: two\n", {"old": "new"}) == "new: one\nother: two\n")
check("values untouched", lambda: _candidate.migrate("title: old\n", {"title": "name", "old": "new"}) == "name: old\n")
check("comments and blanks", lambda: _candidate.migrate("# old: comment\n\nold: value  # old\n", {"old": "new"}) == "# old: comment\n\nnew: value  # old\n")
check("exact key boundary", lambda: _candidate.migrate("old.extra: a\nold: b\n", {"old": "new"}) == "old.extra: a\nnew: b\n")
check("sentinel at start", lambda: _candidate.migrate("# FROZEN BELOW\nold: keep\n", {"old": "new"}) == "# FROZEN BELOW\nold: keep\n")
check("no sentinel", lambda: _candidate.migrate("a: 1\nb: 2\n", {"a": "x"}) == "x: 1\nb: 2\n")
check("keys split", lambda: _candidate.keys("a: 1\n# FROZEN BELOW\nb: 2\n", False) == ["a"] and _candidate.keys("a: 1\n# FROZEN BELOW\nb: 2\n") == ["a", "b"])
check("migration count", lambda: _candidate.migration_count("a: 1\na: 2\n# FROZEN BELOW\na: 3\n", {"a": "z"}) == 2 and _candidate.migration_count("a: 1\na: 2\n# FROZEN BELOW\na: 3\n", {"a": "z"}, True) == 3)
check("frozen and tail", lambda: _candidate.has_frozen_tail("a: 1\n# FROZEN BELOW\n") is True and _candidate.has_frozen_tail("a: 1\n") is False and _candidate.unchanged_tail("a: 1\n# FROZEN BELOW\na: 2\n", "x: 1\n# FROZEN BELOW\na: 2\n") is True)
check("batch order", lambda: _candidate.migrate_many(["a: 1\n", "b: 2\n"], {"a": "x", "b": "y"}) == ["x: 1\n", "y: 2\n"])
report()
