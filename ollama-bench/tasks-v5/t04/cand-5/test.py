import os
import re
import sys
import threading

TOTAL = 5
_ora_fails = []
_ora_done = 0
_ora_lock = threading.Lock()
_ora_parsed = None


def _ora_check(name, fn):
    global _ora_done
    try:
        ok = bool(fn())
    except Exception as exc:
        ok = False
        name = "%s raised %s" % (name, type(exc).__name__)
    if not ok:
        _ora_fails.append(name)
    with _ora_lock:
        _ora_done += 1


def _ora_watchdog():
    n = max(0, min(TOTAL, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_parse_answer():
    try:
        with open("answer.txt", "r", encoding="utf-8", newline=None) as handle:
            raw = handle.read()
    except Exception:
        return None
    lines = raw.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    lines = [line.rstrip() for line in lines]
    if len(lines) != 3:
        return None
    if not lines[0].startswith("PATH: ") or not lines[1].startswith("LINES: "):
        return None
    if not lines[2].startswith("EXPLANATION: "):
        return None
    path = lines[0][6:].strip()
    raw_span = lines[1][7:].strip()
    explanation = lines[2][13:].strip().casefold()
    if path == "NONE":
        span = "NONE" if raw_span == "NONE" else None
    else:
        match = re.fullmatch(r"([1-9][0-9]*)-([1-9][0-9]*)", raw_span)
        span = (int(match.group(1)), int(match.group(2))) if match else None
        if span is not None and span[0] > span[1]:
            span = None
    if not path or span is None or not explanation:
        return None
    return path, span, explanation


def _ora_mentions_all_steps(text):
    groups = (
        ("canonical", "normalize", "identity"),
        ("failed", "failure"),
        ("60", "sixty", "seconds", "second"),
        ("before", "prior"),
        ("verify", "credential"),
        ("success", "successful", "succeed"),
        ("clear", "remove", "reset", "lift"),
        ("other", "each", "only", "identity-specific", "identity"),
    )
    return all(any(word in text for word in group) for group in groups)


def _ora_report():
    n = max(0, min(TOTAL, TOTAL - len(_ora_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("PASS" if not _ora_fails else "FAIL %s" % _ora_fails[:10])
    if _ora_parsed is not None and not _ora_fails:
        verdict = "correct"
    elif _ora_parsed is not None and _ora_parsed[0] != "NONE":
        verdict = "confidently_wrong"
    else:
        verdict = "visibly_failed"
    print("VERDICT %s" % verdict)
    sys.exit(0 if not _ora_fails else 1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()

_ora_parsed = _ora_parse_answer()
_ora_check("strict answer format", lambda: _ora_parsed is not None)
_ora_check("production implementation", lambda: _ora_parsed is not None and
            _ora_parsed[0] == "app/request_path.py")
# The span must sit inside process_login (lines 6-20) and cover all three required
# operations: the pre-verification lockout check (9-11), the 60 s record (13-17) and the
# clear on success (18). The prompt tells the model to cite "the implementation itself, not
# a ... declaration", so excluding the `def` line and the docstring is a correct reading and
# must not be scored as a wrong answer. A shotgun span still fails on the 6 <= first bound.
_ora_check("contiguous implementation span", lambda: _ora_parsed is not None and
            isinstance(_ora_parsed[1], tuple) and
            6 <= _ora_parsed[1][0] <= 9 and 18 <= _ora_parsed[1][1] <= 20)
_ora_check("explanation covers serial behavior", lambda: _ora_parsed is not None and
            _ora_mentions_all_steps(_ora_parsed[2]))
_ora_check("positive decision", lambda: _ora_parsed is not None and _ora_parsed[0] != "NONE")
_ora_report()
