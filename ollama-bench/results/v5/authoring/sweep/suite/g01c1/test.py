import contextlib
import io
import os
import sys
import threading


TOTAL = 24
_fails = []
_done = 0
_lock = threading.Lock()
_runtime_error = False
_well_formed = True


def _check(name, fn):
    global _done, _runtime_error, _well_formed
    try:
        ok = fn()
    except BaseException as exc:
        ok = False
        _runtime_error = True
        name = "%s raised %s" % (name, type(exc).__name__)
    if not ok:
        _fails.append(name)
    with _lock:
        _done += 1


def _report():
    _timer.cancel()
    score = max(0, min(TOTAL, TOTAL - len(_fails)))
    print("SCORE %d/%d" % (score, TOTAL))
    if _fails:
        print("FAIL", _fails[:10])
        verdict = "visibly_failed" if _runtime_error or not _well_formed else "confidently_wrong"
    else:
        print("PASS")
        verdict = "correct"
    print("VERDICT", verdict)
    sys.exit(0 if not _fails else 1)


def _watchdog():
    with _lock:
        finished = _done
        failed = len(_fails)
    score = max(0, min(TOTAL, finished - failed))
    print("SCORE %d/%d" % (score, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _watchdog)
_timer.daemon = True
_timer.start()

try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import transform as _candidate
    _candidate_transform = _candidate.transform
except BaseException as _exc:
    _fails = ["import failed: %s" % type(_exc).__name__] + ["not run"] * (TOTAL - 1)
    _runtime_error = True
    _report()


def _ora_record(record):
    if record == "":
        return ""
    absolute = record.startswith("/")
    trailing = record.endswith("/")
    parts = []
    for segment in record.split("/"):
        if segment == "" or segment == ".":
            continue
        if segment == "..":
            for index in range(len(parts) - 1, -1, -1):
                if parts[index] != "..":
                    del parts[index]
                    break
            else:
                if not absolute:
                    parts.append("..")
        else:
            parts.append(segment)
    if parts:
        answer = ("/" if absolute else "") + "/".join(parts)
        return answer + "/" if trailing else answer
    return "/" if absolute else "."


def _ora_transform(text):
    return "\n".join(_ora_record(record) for record in text.split("\n"))


_CASES = [
    ("basic segments", "a/b/./c"),
    ("collapse interior empties", "a///b////c"),
    ("absolute and parent", "/a/b/../c"),
    ("relative parent", "a/b/../../c"),
    ("relative excess parents", "a/../../b"),
    ("absolute excess parents", "/a/../../b"),
    ("empty record", ""),
    ("empty records around LF", "\n\n"),
    ("ending LF", "a/b\n"),
    ("trailing slash", "a/b//"),
    ("trailing slash after parent", "/a/b/../"),
    ("relative dot only", "././"),
    ("absolute root noise", "////.//..///"),
    ("double leading slash", "//server///share"),
    ("parent before ordinary", "../../a/b"),
    ("parent then cancellation", "../a/../b"),
    ("punctuation preserved", "a-1/hello.world/../x_y"),
    ("spaces are data", " two words /../ final "),
    ("unicode is data", "café/東京/../δοκιμή"),
    ("carriage return is data", "a\r/b\r/"),
    ("LF with absolute record", "x\n///a//b/"),
    ("all discarded relative", ".//./..//.."),
    ("all discarded absolute", "/.//..//../"),
    ("ordinary named dot", ".../.../..hidden/../z/"),
]


def _make_check(name, source):
    def run():
        global _well_formed
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            got = _candidate_transform(source)
        if not isinstance(got, str):
            _well_formed = False
            return False
        return got == _ora_transform(source)
    return lambda: run()


for _name, _source in _CASES:
    _check(_name, _make_check(_name, _source))

_report()
