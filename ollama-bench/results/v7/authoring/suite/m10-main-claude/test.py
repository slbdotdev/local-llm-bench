import os
import sys
import threading

_ora_total = 9
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
    # clamped: a verdict override may append a reason beyond the subcheck count, and a
    # negative score is a grader artifact rather than a result.
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %d/%d" % (n, _ora_total))
    if _ora_verdict_override:
        if not _ora_fails:
            print("FAIL []")
        else:
            print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        sys.exit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    sys.exit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()

import json
import shutil
import subprocess

CSV = os.path.join("report", "limits.csv")
PROG = os.path.join("tools", "build_limits.py")


def _excluded():
    """Stages on Platform Reliability's rota, read where the tree records it and nowhere else.

    Derived rather than hardcoded on purpose: subcheck 9 mutates the manifest and requires the
    CSV to follow, and an expectation built from literals could not tell a real program from a
    printed table (D7-20).
    """
    with open(os.path.join("docs", "operations.md"), encoding="utf-8") as fh:
        text = fh.read()
    out = set()
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[3] == "Platform Reliability":
            out.add(cells[0])
    return out


def _covered(man):
    skip = _excluded()
    return [s for s in man["stages"] if s["name"] not in skip]


def _expected(manifest_path=os.path.join("config", "manifest.json")):
    with open(manifest_path, encoding="utf-8") as fh:
        man = json.load(fh)
    rows = sorted(_covered(man), key=lambda s: (-s["limit"], s["name"]))
    return ("stage,limit,window_s\n" + "".join(
        "%s,%d,%d\n" % (s["name"], s["limit"], s["window_s"]) for s in rows))


def _read(path):
    """Decode without normalising line endings.

    The prompt states LF line endings in terms, so silently accepting CRLF was a false
    acceptance of a stated rule. A BOM is still tolerated: the prompt is silent about it.
    """
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8-sig")


def _lf_only(path):
    with open(path, "rb") as fh:
        return b"\r" not in fh.read()


def _run_prog():
    r = subprocess.run([sys.executable, PROG], capture_output=True, timeout=30)
    return r.returncode == 0


def _snapshot():
    """The bytes of the deliverable, so a check that runs the program can put them back.

    A grader is allowed to run the solver's work; it is not allowed to destroy the work it is
    grading. Without this, grading the same sandbox twice turns a correct answer into a
    confidently wrong one, because the first grading leaves the CSV holding the numbers the
    second subcheck fabricated (D7-15).
    """
    if not os.path.exists(CSV):
        return None
    with open(CSV, "rb") as fh:
        return fh.read()


def _restore(blob):
    if blob is None:
        if os.path.exists(CSV):
            os.remove(CSV)
        return
    d = os.path.dirname(CSV)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(CSV, "wb") as fh:
        fh.write(blob)


def _regenerates():
    """Delete the CSV, run the program, and require it back and correct."""
    if not os.path.exists(PROG):
        return False
    keep = _snapshot()
    try:
        os.remove(CSV)
        if not _run_prog():
            return False
        return os.path.exists(CSV) and _read(CSV) == _expected()
    finally:
        _restore(keep)


def _derives_from_the_manifest():
    """Change one limit in a COPY of the manifest, regenerate, and require the CSV to follow.

    A program that prints a literal table passes every other check and fails this one.
    """
    _keep_csv = _snapshot()
    shutil.copy(os.path.join("config", "manifest.json"), "_ora_manifest.bak")
    try:
        with open(os.path.join("config", "manifest.json"), encoding="utf-8") as fh:
            man = json.load(fh)
        man["stages"][0]["limit"] = 100000
        with open(os.path.join("config", "manifest.json"), "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(man, fh, indent=2)
            fh.write("\n")
        want = _expected()
        if os.path.exists(CSV):
            os.remove(CSV)
        if not _run_prog():
            return False
        return os.path.exists(CSV) and _read(CSV) == want
    finally:
        shutil.move("_ora_manifest.bak", os.path.join("config", "manifest.json"))
        _restore(_keep_csv)


_csv_present = os.path.exists(CSV)
_prog_present = os.path.exists(PROG)
_ora_shape = _csv_present

_first = _read(CSV) if _csv_present else ""

_ora_check("report/limits.csv exists", lambda: _csv_present)
_ora_check("the CSV header is exactly the one specified",
           lambda: _first.split("\n")[0] == "stage,limit,window_s")
_ora_check("the CSV has one line per covered stage plus a header",
           lambda: len([x for x in _first.split("\n") if x]) ==
                   1 + len(_covered(json.load(open(os.path.join("config", "manifest.json"),
                                                   encoding="utf-8")))))
_ora_check("the CSV content and ordering are exactly right",
           lambda: _first == _expected())
_ora_check("the CSV ends with a final newline",
           lambda: _csv_present and _read(CSV).endswith("\n"))
_ora_check("the CSV uses the LF line endings the prompt requires",
           lambda: _csv_present and _lf_only(CSV))
_ora_check("tools/build_limits.py exists", lambda: _prog_present)
_ora_check("running the program from scratch reproduces the CSV", _regenerates)
_ora_check("the program derives the CSV from the manifest it reads",
           _derives_from_the_manifest)

_ora_report()
