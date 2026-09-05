import os
import sys
import threading

_ora_total = 5
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

import re

CODE = "RN-208"
SLOT = 67
WITHDRAWN = ("RN-114", "RN-118", "RN-121", "RN-127", "RN-133")


def _lines():
    with open("answer.txt", "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8-sig", "replace").replace("\r\n", "\n").replace("\r", "\n")
    # Blank lines are NOT dropped: the prompt fixes the file at exactly two lines,
    # so a four-line answer must not pass a two-line contract.
    return [ln.strip() for ln in text.strip("\n").split("\n")]


try:
    _ls = _lines()
except Exception:
    _ls = []

_ora_shape = (len(_ls) == 2
              and _ls[0].upper().startswith("ESCALATION:")
              and _ls[1].upper().startswith("SLOT:"))


def _field(prefix):
    for ln in _ls:
        if ln.upper().startswith(prefix):
            return ln.split(":", 1)[1].strip()
    return None


_ora_check("answer.txt has exactly the two required lines", lambda: _ora_shape)
_ora_check("the escalation line names the code currently in force",
           lambda: _field("ESCALATION:") == CODE)
_ora_check("the escalation line does not name a withdrawn code",
           lambda: _field("ESCALATION:") not in WITHDRAWN)
_ora_check("the slot line names the active reconcile slot",
           lambda: _field("SLOT:") is not None and re.fullmatch(r"\d+", _field("SLOT:"))
                   and int(_field("SLOT:")) == SLOT)
_ora_check("the slot number is written without leading zeros",
           lambda: _field("SLOT:") == str(SLOT))

_ora_report()
