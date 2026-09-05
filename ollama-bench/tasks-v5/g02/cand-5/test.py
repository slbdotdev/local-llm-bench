import hashlib
import json
import os
import sys
import threading

TOTAL = 15
fails = []
done = 0
runtime_bad = False
_lock = threading.Lock()
_TEST_SHA256 = "e11cfa21e19f9d24712ed0af195383b2c7c6c76f2f30fda47fec6586d04c0e6e"
_SEED_SHA256 = {"releaseplan/planner.py": "c1d4790392559a087e494b53175fa165ebab6774ddef42391613c97ff7d8a08f"}


def _ora_normal(data):
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _ora_candidate_worked():
    for path, expected in _SEED_SHA256.items():
        try:
            with open(path, "rb") as handle:
                actual = hashlib.sha256(_ora_normal(handle.read())).hexdigest()
        except OSError:
            return True
        if actual != expected:
            return True
    return False


def _ora_json(value):
    return json.dumps(value, separators=(",", ":"))


def _ora_plan(catalog, lock, policy, history, target, platform, release):
    aliases = dict((r["old"], r["new"]) for r in history)

    def canon(name):
        seen = set()
        while name in aliases and release >= next(
                r["effective"] for r in history if r["old"] == name):
            if name in seen:
                raise ValueError("cycle")
            seen.add(name)
            name = aliases[name]
        return name

    target = canon(target)
    if target not in catalog or target not in lock:
        return []
    selected = []
    seen = set()

    def allowed(name):
        record = catalog.get(name)
        if record is None or name not in lock:
            return False
        if "*" not in record.get("platforms", ["*"]) and platform not in record["platforms"]:
            return False
        active = [r for r in policy if r["package"] == name
                  and r.get("platform", "*") in ("*", platform)
                  and r.get("start", "0000-00") <= release < r.get("end", "9999-99")]
        if not active:
            return True
        active.sort(key=lambda r: (int(r.get("revision", 0)),
                                   r.get("platform", "*") == platform))
        return active[-1]["effect"] == "allow"

    def visit(name):
        name = canon(name)
        if name in seen:
            return
        seen.add(name)
        if name not in lock:
            raise KeyError(name)
        for dep in lock[name].get("deps", []):
            visit(dep)
        selected.append(name)

    visit(target)
    if any(not allowed(name) for name in selected):
        return []
    return selected


def _ora_render(catalog, lock, policy, history, target, platform, release):
    names = _ora_plan(catalog, lock, policy, history, target, platform, release)
    if not names:
        return ""
    def canon(name):
        changed = True
        while changed:
            changed = False
            for row in history:
                if row["old"] == name and release >= row["effective"]:
                    name, changed = row["new"], True
                    break
        return name
    target = canon(target)
    lines = ["release=%s platform=%s" % (release, platform), "target=" + target]
    lines += ["- %s@%s requires=%s" % (name, lock[name]["version"], ",".join(lock[name]["deps"]))
              for name in names]
    return "\n".join(lines) + "\n"


def _ora_small():
    catalog = [{"name": "app", "version": "9.9", "deps": [], "platforms": ["*"], "priority": 1}]
    lock = [{"name": "app", "version": "1.0", "deps": []}]
    return _ora_json(catalog), _ora_json(lock), "[]", "[]"


def _ora_fixture():
    rows = []
    for index in range(0, 7):
        with open(os.path.join("data", "catalog-%d.json" % index), encoding="utf-8") as handle:
            rows.extend(json.load(handle))
    with open(os.path.join("data", "lock.json"), encoding="utf-8") as handle:
        lock = json.load(handle)
    with open(os.path.join("data", "policy.json"), encoding="utf-8") as handle:
        policy = json.load(handle)
    history = []
    for year in range(2019, 2028):
        with open(os.path.join("docs", "history", str(year) + ".json"), encoding="utf-8") as handle:
            history.extend(json.load(handle))
    with open(os.path.join("data", "history-current.json"), encoding="utf-8") as handle:
        history.extend(json.load(handle))
    return rows, lock, policy, history


def _ora_check(name, fn):
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


def _ora_watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_report():
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


timer = threading.Timer(45.0, _ora_watchdog)
timer.daemon = True
timer.start()
try:
    import releaseplan as _candidate
    from releaseplan import compat as _compat
except Exception as exc:
    runtime_bad = True
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    _ora_report()


_ora_check("test file is unchanged", lambda: hashlib.sha256(
    open(os.path.join("tests", "test_planner.py"), "rb").read()).hexdigest() == _TEST_SHA256)

_ora_check("basic positive example", lambda: _candidate.build_plan(*_ora_small(), "app", "linux", "2025-03")
           == "release=2025-03 platform=linux\ntarget=app\n- app@1.0 requires=\n")
_ora_check("explicit negative policy", lambda: _candidate.build_plan(
    *_ora_small()[:2], '[{"package":"app","platform":"*","effect":"deny","start":"0000-00","end":"9999-99","revision":1}]', "[]", "app", "linux", "2025-03") == "")
_ora_check("dependency closure", lambda: _candidate.plan_records(
    _ora_json([{"name":"app","version":"1","deps":["lib"],"platforms":["*"]},{"name":"lib","version":"1","deps":[],"platforms":["*"]}]),
    _ora_json([{"name":"app","version":"7","deps":["lib"]},{"name":"lib","version":"8","deps":[]}]), "[]", "[]", "app", "linux", "2025-03") == ["lib", "app"])
_ora_check("exact platform beats wildcard", lambda: _candidate.plan_records(
    _ora_small()[0], _ora_small()[1],
    _ora_json([{ "package":"app","platform":"*","effect":"deny","start":"0000-00","end":"9999-99","revision":2},{"package":"app","platform":"windows","effect":"allow","start":"0000-00","end":"9999-99","revision":2}]), "[]", "app", "windows", "2025-03") == ["app"])
_ora_check("wildcard deny applies", lambda: _candidate.plan_records(*_ora_small()[:2],
    _ora_json([{ "package":"app","platform":"*","effect":"deny","start":"0000-00","end":"9999-99","revision":2}]), "[]", "app", "linux", "2025-03") == [])
_ora_check("half open window", lambda: _candidate.plan_records(*_ora_small()[:2],
    _ora_json([{ "package":"app","platform":"*","effect":"deny","start":"2025-01","end":"2025-03","revision":2}]), "[]", "app", "linux", "2025-03") == ["app"])
_ora_check("repeated alias", lambda: _candidate.plan_records(*_ora_small()[:2], "[]",
    _ora_json([{ "old":"old-app","new":"older-app","effective":"2024-01"},{"old":"older-app","new":"app","effective":"2025-01"}]), "old-app", "linux", "2025-03") == ["app"])
_ora_check("missing dependency is negative", lambda: _candidate.plan_records(
    _ora_json([{ "name":"app","version":"1","deps":["gone"],"platforms":["*"]}]),
    _ora_json([{ "name":"app","version":"1","deps":["gone"]}]), "[]", "[]", "app", "linux", "2025-03") == [])
_ora_check("unavailable target is negative", lambda: _candidate.plan_records(
    _ora_json([{ "name":"app","version":"1","deps":[],"platforms":["bsd"]}]),
    _ora_json([{ "name":"app","version":"1","deps":[]}]), "[]", "[]", "app", "linux", "2025-03") == [])
_ora_check("pinned rendering", lambda: _candidate.build_plan(*_ora_small(), "app", "linux", "2025-03").endswith("- app@1.0 requires=\n"))
_ora_check("catalog version is advisory", lambda: "@9.9" not in
           _candidate.build_plan(*_ora_small(), "app", "linux", "2025-03"))
_ora_check("compatibility alias", lambda: _compat.make_plan(*_ora_small(), "app", "linux", "2025-03")
           == _candidate.build_plan(*_ora_small(), "app", "linux", "2025-03"))
_ora_check("empty helper", lambda: _compat.is_empty_plan(""))
_ora_check("all catalog shards", lambda: len(_candidate.plan_records(
    _ora_json(_ora_fixture()[0]), _ora_json(_ora_fixture()[1]), _ora_json(_ora_fixture()[2]),
    _ora_json(_ora_fixture()[3]), "pkg-280", "linux", "2028-01")) == 280)
_ora_report()
