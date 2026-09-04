import hashlib
import importlib
import os
import sys
import threading

TOTAL = 12
fails = []
done = 0
runtime_bad = False
module_ok = False
_lock = threading.Lock()
_TEST_SHA256 = "1acc855760c1a90e973542281af42c34a0d70771dacd3e63e59b7646a5aeb7df"
# Hash the pristine implementation so an untouched candidate is a visible failure.
_SEED_SHA256 = {
    "manifest.py": "0655bcfbc9b4748c43f91a76fb7598c91f8213768cd06d75b13391f3e7e85037",
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
    verdict = ("visibly_failed" if runtime_bad or not _candidate_worked()
               else "confidently_wrong")
    print("VERDICT", verdict)
    sys.exit(1)


timer = threading.Timer(45.0, _watchdog)
timer.daemon = True
timer.start()

try:
    import manifest as _candidate
    module_ok = True
except Exception as exc:
    runtime_bad = True
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    report()


def _ora_rewrite(text, updates):
    lines = text.splitlines()
    trailing = text.endswith("\n")
    current = ""
    used = set()
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip()
            out.append(line)
            continue
        if line.lstrip().startswith("#") or "=" not in line:
            out.append(line)
            continue
        before, rest = line.split("=", 1)
        leading = before[:len(before) - len(before.lstrip())]
        key = before.strip()
        between = before[len(leading) + len(key):]
        after_equals = rest[:len(rest) - len(rest.lstrip())]
        hit = next((pair for pair in updates
                    if pair[0].strip().casefold() == current.casefold()
                    and pair[1].strip().casefold() == key.casefold()), None)
        if hit is None:
            out.append(line)
        else:
            out.append(leading + key + between + "=" + after_equals + str(updates[hit]))
            used.add(hit)
    for pair, value in updates.items():
        if pair in used:
            continue
        section, key = pair
        at = next((i for i, line in enumerate(out)
                   if line.strip().casefold() == ("[" + section + "]").casefold()), None)
        if at is None:
            if out and out[-1] != "":
                out.append("")
            out.extend(["[" + section + "]", key + "=" + str(value)])
        else:
            end = next((i for i in range(at + 1, len(out))
                        if out[i].strip().startswith("[") and out[i].strip().endswith("]")), len(out))
            while end > at + 1 and out[end - 1].strip() == "":
                end -= 1
            out.insert(end, key + "=" + str(value))
    return "\n".join(out) + ("\n" if trailing else "")


def _ora_test_hash():
    with open("test_manifest.py", "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest() == _TEST_SHA256


source = "[Deploy]\nTimeout = 30\nName = Release\n"
check("test file is unchanged", _ora_test_hash)
check("case-insensitive update", lambda: _candidate.rewrite(source, {("deploy", "timeout"): 45}) == _ora_rewrite(source, {("deploy", "timeout"): 45}))
check("all duplicate records", lambda: _candidate.rewrite("[a]\nx=1\nx=2\n", {("A", "X"): 9}) == "[a]\nx=9\nx=9\n")
check("insert into section", lambda: _candidate.rewrite("[app]\nname=demo\n", {("APP", "port"): 80}) == "[app]\nname=demo\nport=80\n")
check("create section", lambda: _candidate.rewrite("[app]\nname=demo\n", {("worker", "threads"): 2}) == "[app]\nname=demo\n\n[worker]\nthreads=2\n")
check("preserve comments and spacing", lambda: _candidate.rewrite("# h\n[app]\n  Port = 8080\n\n# k\n", {("app", "port"): 9000}) == "# h\n[app]\n  Port = 9000\n\n# k\n")
check("scope sections", lambda: _candidate.rewrite("[a]\nx=1\n[b]\nx=2\n", {("A", "x"): 7}) == "[a]\nx=7\n[b]\nx=2\n")
check("last value lookup", lambda: _candidate.values("[App]\nmode=old\nmode=new\n", "app") == {"mode": "new"})
check("unique sections", lambda: _candidate.sections("[App]\nx=1\n[app]\ny=2\n[Other]\nz=3\n") == ["App", "Other"])
check("scoped removal", lambda: _candidate.remove_keys("[a]\nx=1\ny=2\n[b]\nx=3\n", [("A", "X")]) == "[a]\ny=2\n[b]\nx=3\n")
check("overlay order", lambda: _candidate.overlay(["[a]\nx=1\n", "[b]\ny=2\n"], {("a", "x"): 4}) == ["[a]\nx=4\n", "[b]\ny=2\n\n[a]\nx=4\n"])
check("prefix names are scoped", lambda: _candidate.rewrite("[app]\nx=1\n[application]\nx=2\n", {("app", "x"): 7}) == "[app]\nx=7\n[application]\nx=2\n")
report()
