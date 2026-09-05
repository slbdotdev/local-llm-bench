import os
import sys
import threading
from pathlib import Path

_ORA_EXPECTED = {
    ("index.md", 3): "UPDATE",
    ("archive/incident-2026-01.md", 3): "LEAVE",
    ("archive/release-2025.md", 3): "LEAVE",
    ("runbooks/deploy-check.md", 5): "UPDATE",
}
_ORA_OLD = "repo/tools/deploy/check.py"
_ORA_NEW = "repo/tools/release/check.py"
_ORA_TOTAL = 8
_fails = []
_done = 0
_lock = threading.Lock()


def _ora_watchdog():
    score = max(0, min(_ORA_TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()


def _ora_parse():
    try:
        raw = Path("reference_audit.txt").read_text(encoding="utf-8")
    except Exception:
        return None
    # A single trailing newline is optional. The prompt never says whether the file
    # must end in a newline, so both forms are correct and scoring one of them as
    # visibly_failed mislabels a correct answer, which would corrupt the section 6
    # instrument. Everything else stays strict: no blank lines, exact line count.
    # Normalise only what the prompt does not specify: a BOM, the line-ending
    # convention, and leading/trailing blank lines. Trailing whitespace INSIDE a line
    # is left alone on purpose -- the fields are tab-separated and the last one is a
    # replacement string the prompt requires verbatim, so a space there is real content.
    if raw.startswith("\ufeff"):
        raw = raw[1:]
    body = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = body.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) != len(_ORA_EXPECTED) or any(not ln for ln in lines):
        return None
    got = {}
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 5 or fields[0] not in ("UPDATE", "LEAVE"):
            return None
        action, filename, line_no, old, replacement = fields
        if (not filename or filename.startswith("/") or filename.startswith("./")
                or ".." in filename.split("/") or not line_no.isdigit()
                or int(line_no) < 1 or old != _ORA_OLD):
            return None
        key = (filename, int(line_no))
        if key in got or key not in _ORA_EXPECTED:
            return None
        if action == "UPDATE" and replacement != _ORA_NEW:
            return None
        if action == "LEAVE" and replacement != "-":
            return None
        got[key] = action
    return got if set(got) == set(_ORA_EXPECTED) else None


def _ora_finish(parsed):
    global _done
    if parsed is None:
        print("SCORE 0/%d" % _ORA_TOTAL)
        print("FAIL [unparseable reference_audit.txt]")
        print("VERDICT visibly_failed")
        sys.exit(1)
    tp = fn = fp = tn = score = 0
    for key, expected in _ORA_EXPECTED.items():
        predicted = parsed[key]
        if expected == "UPDATE" and predicted == "UPDATE":
            tp += 1
            score += 2
        elif expected == "UPDATE":
            fn += 1
            score += 1
            _fails.append("%s:%d_missed_update" % key)
        elif predicted == "LEAVE":
            tn += 1
            score += 2
        else:
            fp += 1
            _fails.extend(["%s:%d_false_positive_update" % key,
                           "%s:%d_history_damaged" % key])
        with _lock:
            _done += 2
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    if _fails:
        print("FAIL [" + ", ".join(_fails) + "] confusion TP=%d FN=%d FP=%d TN=%d"
              % (tp, fn, fp, tn))
        print("VERDICT confidently_wrong")
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


try:
    _ora_finish(_ora_parse())
finally:
    _timer.cancel()
