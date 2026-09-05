import os
import sys
import threading

_ora_total = 8
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


def _expected(manifest_path=os.path.join("config", "manifest.json")):
    with open(manifest_path, encoding="utf-8") as fh:
        man = json.load(fh)
    rows = sorted(man["stages"], key=lambda s: (-s["limit"], s["name"]))
    return ("stage,limit,window_s\n" + "".join(
        "%s,%d,%d\n" % (s["name"], s["limit"], s["window_s"]) for s in rows))


def _read(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8-sig").replace("\r\n", "\n")


def _run_prog():
    r = subprocess.run([sys.executable, PROG], capture_output=True, timeout=30)
    return r.returncode == 0


def _regenerates():
    """Delete the CSV, run the program, and require it back and correct."""
    if not os.path.exists(PROG):
        return False
    os.remove(CSV)
    if not _run_prog():
        return False
    return os.path.exists(CSV) and _read(CSV) == _expected()


def _derives_from_the_manifest():
    """Change one limit in a COPY of the manifest, regenerate, and require the CSV to follow.

    A program that prints a literal table passes every other check and fails this one.
    """
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


_csv_present = os.path.exists(CSV)
_prog_present = os.path.exists(PROG)
_ora_shape = _csv_present

_first = _read(CSV) if _csv_present else ""

_ora_check("report/limits.csv exists", lambda: _csv_present)
_ora_check("the CSV header is exactly the one specified",
           lambda: _first.split("\n")[0] == "stage,limit,window_s")
_ora_check("the CSV has one line per stage plus a header",
           lambda: len([x for x in _first.split("\n") if x]) ==
                   1 + len(json.load(open(os.path.join("config", "manifest.json"),
                                          encoding="utf-8"))["stages"]))
_ora_check("the CSV content and ordering are exactly right",
           lambda: _first == _expected())
_ora_check("the CSV ends with a final newline",
           lambda: _csv_present and _read(CSV).endswith("\n"))
_ora_check("tools/build_limits.py exists", lambda: _prog_present)
_ora_check("running the program from scratch reproduces the CSV", _regenerates)
_ora_check("the program derives the CSV from the manifest it reads",
           _derives_from_the_manifest)

_ora_report()
