import os
import sys
import threading


INITIAL = {
    os.path.join("config", "formatting.ini"): b"# Configuraci\xc3\xb3n del cat\xc3\xa1logo\r\nwelcome=Ol\xc3\xa1, cat\xc3\xa1logo\r\nmode=leg\xc3\xadvel\r\n",
    os.path.join("docs", "operator_notes.txt"): b"owner=Zo\xc3\xab\r\nnote=Revisi\xc3\xb3n pendiente\r\nestado=vigente\r\n",
}
EXPECTED = {
    os.path.join("config", "formatting.ini"): [b"# Configuraci\xc3\xb3n del cat\xc3\xa1logo", b"welcome=Ol\xc3\xa1, cat\xc3\xa1logo \xe2\x80\x94 listo", b"mode=leg\xc3\xadvel"],
    os.path.join("docs", "operator_notes.txt"): [b"owner=Zo\xc3\xab", b"note=Revisi\xc3\xb3n completa", b"estado=vigente"],
}
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
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %d/%d" % (n, _ora_total))
    if _ora_verdict_override:
        print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        raise SystemExit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        raise SystemExit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    raise SystemExit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()


def normalized(data):
    if b"\r\n" not in data or b"\n" in data.replace(b"\r\n", b""):
        return None
    lines = data.split(b"\r\n")
    while lines and lines[0].strip(b" \t") == b"":
        lines.pop(0)
    while lines and lines[-1].strip(b" \t") == b"":
        lines.pop()
    return [line.rstrip(b" \t") for line in lines]


def main():
    global _ora_shape
    root = os.getcwd()
    data = {}
    for relative in EXPECTED:
        with open(os.path.join(root, relative), "rb") as handle:
            data[relative] = handle.read()
    _ora_shape = any(data[relative] != INITIAL[relative] for relative in EXPECTED)
    config_path = os.path.join("config", "formatting.ini")
    notes_path = os.path.join("docs", "operator_notes.txt")
    _ora_check("formatting config preserves CRLF", lambda: normalized(data[config_path]) is not None)
    _ora_check("formatting config has the expected lines", lambda: set(normalized(data[config_path])) == set(EXPECTED[config_path]))
    _ora_check("formatting config preserves UTF-8 content", lambda: b"Configuraci\xc3\xb3n" in data[config_path] and b"\xe2\x80\x94" in data[config_path])
    _ora_check("operator notes preserves CRLF", lambda: normalized(data[notes_path]) is not None)
    _ora_check("operator notes has the expected lines", lambda: set(normalized(data[notes_path])) == set(EXPECTED[notes_path]))
    _ora_report()


try:
    main()
except SystemExit:
    raise
except Exception:
    while _ora_done < _ora_total:
        _ora_check("grader setup", lambda: False)
    _ora_report()
