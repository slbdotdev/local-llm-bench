import os
import re
import sys
import threading

TOTAL = 4
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = bool(fn())
    except Exception as exc:
        ok = False
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
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("PASS" if not fails else "FAIL %s" % fails[:10])
    if _ora_parsed is not None and not fails:
        verdict = "correct"
    elif _ora_parsed is not None and _ora_parsed[0] != "NONE":
        verdict = "confidently_wrong"
    else:
        verdict = "visibly_failed"
    print("VERDICT", verdict)
    sys.exit(0 if not fails else 1)


_timer = threading.Timer(45.0, _watchdog)
_timer.daemon = True
_timer.start()


def _ora_read_answer():
    try:
        with open("answer.txt", "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except Exception:
        return None
    if len(lines) != 3 or not lines[0].startswith("PATH: "):
        return None
    if not lines[1].startswith("LINES: ") or not lines[2].startswith("EXPLANATION: "):
        return None
    path = lines[0][6:]
    raw_span = lines[1][7:]
    explanation = lines[2][13:].strip()
    if path == "NONE":
        span = "NONE" if raw_span == "NONE" else None
    else:
        match = re.fullmatch(r"([1-9][0-9]*)-([1-9][0-9]*)", raw_span)
        span = (int(match.group(1), 10), int(match.group(2), 10)) if match else None
        if span is not None and span[0] > span[1]:
            span = None
    if not path or span is None or not explanation:
        return None
    return path, span, explanation.casefold()


def _ora_explains_negative(text):
    groups = (
        ("no", "not", "nowhere", "nothing"),
        ("implement", "code", "present"),
        ("account", "identity", "user"),
        ("timed", "60", "second", "cooldown"),
        ("reset", "success", "successful", "lift"),
    )
    return all(any(word in text for word in group) for group in groups)


_ora_parsed = _ora_read_answer()
check("strict answer format", lambda: _ora_parsed is not None)
check("negative finding", lambda: _ora_parsed is not None and _ora_parsed[0] == "NONE" and _ora_parsed[1] == "NONE")
check("explanation", lambda: _ora_parsed is not None and _ora_parsed[0] == "NONE" and _ora_explains_negative(_ora_parsed[2]))
check("no positive citation", lambda: _ora_parsed is not None and _ora_parsed[0] == "NONE")
report()
