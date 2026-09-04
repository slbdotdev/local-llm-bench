import os
import sys
import threading
from pathlib import Path

_ORA_EXPECTED = {
    ("README.md", 3): "UPDATE",
    ("docs/links.md", 5): "UPDATE",
    ("history/2025-move.md", 3): "LEAVE",
    ("history/postmortem.md", 3): "LEAVE",
    ("runbooks/incident.md", 5): "UPDATE",
    ("runbooks/incident.md", 9): "LEAVE",
    ("runbooks/recovery.md", 7): "UPDATE",
}
_ORA_OLD = "/srv/ops/oncall/handbook.md"
_ORA_NEW = "/srv/ops/oncall/runbook.md"
_ORA_TOTAL = 14
_ora_fails = []
_ora_done = 0
_ora_lock = threading.Lock()


def _ora_watchdog():
    score = max(0, min(_ORA_TOTAL, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()


def _ora_parse():
    try:
        raw = Path("reference_audit.txt").read_text(encoding="utf-8")
    except Exception:
        return None
    body = raw[:-1] if raw.endswith("\n") else raw
    lines = body.split("\n")
    if len(lines) != len(_ORA_EXPECTED) or any(not line for line in lines):
        return None
    rows = []
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 5 or fields[0] not in ("UPDATE", "LEAVE"):
            return None
        action, filename, line_no, old, replacement = fields
        if (not filename or filename.startswith(("/", "./", "seed/"))
                or "\\" in filename or ".." in filename.split("/")
                or not line_no.isdigit() or int(line_no) < 1
                or old != _ORA_OLD):
            return None
        key = (filename, int(line_no))
        if key in rows or key not in _ORA_EXPECTED:
            return None
        if action == "UPDATE" and replacement != _ORA_NEW:
            return None
        if action == "LEAVE" and replacement != "-":
            return None
        rows.append(key)
    if rows != sorted(rows) or set(rows) != set(_ORA_EXPECTED):
        return None
    return {key: line.split("\t")[0] for key, line in zip(rows, lines)}


def _ora_finish(parsed):
    global _ora_done
    if parsed is None:
        print("SCORE 0/%d" % _ORA_TOTAL)
        print("FAIL [unparseable reference_audit.txt]")
        print("VERDICT visibly_failed")
        sys.exit(1)
    score = tp = fn = fp = tn = 0
    for key, expected in _ORA_EXPECTED.items():
        predicted = parsed[key]
        if expected == "UPDATE" and predicted == "UPDATE":
            tp += 1
            score += 2
        elif expected == "UPDATE":
            fn += 1
            score += 1
            _ora_fails.append("%s:%d_missed_update" % key)
        elif predicted == "LEAVE":
            tn += 1
            score += 2
        else:
            fp += 1
            _ora_fails.extend(["%s:%d_false_positive_update" % key,
                               "%s:%d_history_damaged" % key])
        with _ora_lock:
            _ora_done += 2
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    if _ora_fails:
        print("FAIL [" + ", ".join(_ora_fails) + "] confusion TP=%d FN=%d FP=%d TN=%d"
              % (tp, fn, fp, tn))
        print("VERDICT confidently_wrong")
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


try:
    _ora_finish(_ora_parse())
finally:
    _ora_timer.cancel()
