import contextlib
import io
import os
import sys
import threading


TOTAL = 24
_fails = []
_done = 0
_lock = threading.Lock()
_visible_failure = False


def _check(name, fn):
    global _done, _visible_failure
    try:
        ok = fn()
    except BaseException:
        ok = False
        _visible_failure = True
    if not ok:
        _fails.append(name)
    with _lock:
        _done += 1


def _watchdog():
    with _lock:
        score = max(0, min(TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (score, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _report():
    _timer.cancel()
    score = max(0, min(TOTAL, TOTAL - len(_fails)))
    print("SCORE %d/%d" % (score, TOTAL))
    if _fails:
        print("FAIL", _fails[:10])
        print("VERDICT", "visibly_failed" if _visible_failure else "confidently_wrong")
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


def _ora_word(ch):
    return ("a" <= ch <= "z" or "A" <= ch <= "Z" or
            "0" <= ch <= "9" or ch == "_")


def _ora_record(record):
    out = []
    quoted = False
    wrapped = 0
    i = 0
    while i < len(record):
        ch = record[i]
        if not quoted and ch == "#" and (i == 0 or record[i - 1] == " "):
            out.append(record[i:])
            break
        if ch == '"':
            slashes = 0
            j = i - 1
            while j >= 0 and record[j] == "\\":
                slashes += 1
                j -= 1
            if slashes % 2 == 0:
                quoted = not quoted
            out.append(ch)
            i += 1
            continue
        if "0" <= ch <= "9":
            start = i
            while i < len(record) and "0" <= record[i] <= "9":
                i += 1
            eligible = (not quoted and
                        (start == 0 or not _ora_word(record[start - 1])) and
                        (i == len(record) or not _ora_word(record[i])))
            run = record[start:i]
            if eligible and wrapped < 2:
                out.extend(("<", run, ">"))
                wrapped += 1
                if wrapped == 2:
                    out.append(record[i:])
                    break
            else:
                out.append(run)
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _ora_transform(text):
    return "\n".join(_ora_record(record) for record in text.split("\n"))


_CASES = [
    ("empty", ""),
    ("two ordinary runs", "plain 12 and 34"),
    ("second-record limit", "one 1 two 22 three 333"),
    ("quoted digits", '"12" 34 56 78'),
    ("odd escaped quote", '"a\\" 12 34" 56'),
    ("even escaped quote", '12\\\\" 34 56'),
    ("three backslashes", '12\\\\\\" 34 56'),
    ("quote closes before active data", '"a\\\\" 1 2" 3'),
    ("hash inside quote", '"# 1" 2 # 3 4'),
    ("hash at record start", "# 1 2"),
    ("hash after punctuation", "x# 1 2"),
    ("hash after tab", "x 1\t# 2 3"),
    ("hash after ASCII space", "x 1 # 2 3"),
    ("blocked underscore", "x 1 2_ 3 4"),
    ("blocked letters", "a12 123 456b 789"),
    ("unicode boundary", "é123 123é 10_ 11"),
    ("limit resets per LF", '"1" 2\n"3" 4 5'),
    ("empty records and ending LF", "one\n\nthree 3\n"),
    ("carriage returns are data", "a\r1\r 2"),
    ("unterminated quote", '"unterminated 1 2'),
    ("adjacent empty quote", '"a"" 1 2'),
    ("escaped quote outside", 'a 1\\" 2 3'),
    ("dot-separated runs", " 0..9 10"),
    ("tab comment boundary", '"# 1" 2\t# 3 4'),
]


_timer = threading.Timer(45.0, _watchdog)
_timer.daemon = True
_timer.start()

try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import solution as _candidate
        _transform = _candidate.transform
except BaseException as _error:
    _fails = ["load solution"] + ["not run"] * (TOTAL - 1)
    _visible_failure = True
    _report()


for _name, _source in _CASES:
    def _run(source=_source):
        global _visible_failure
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = _transform(source)
        if not isinstance(result, str):
            _visible_failure = True
            return False
        return result == _ora_transform(source)
    _check(_name, _run)

_report()
