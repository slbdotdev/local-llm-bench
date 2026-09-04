import os
import re
import sys
import threading


TOTAL = 3
fails = []
done = 0
_lock = threading.Lock()
_verdict = "visibly_failed"


def _ora_check(name, fn):
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


def _ora_report():
    _timer.cancel()
    score = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (score, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        print("VERDICT", _verdict)
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


def _ora_watchdog():
    score = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (score, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _ora_parse_answer():
    try:
        with open("answer.txt", "r", encoding="utf-8") as stream:
            lines = [line.rstrip("\r\n") for line in stream]
    except Exception:
        return None
    lines = [line for line in lines if line.strip()]
    if len(lines) != 2:
        return None
    answer_lines = [line for line in lines if line.startswith("ANSWER:")]
    evidence_lines = [line for line in lines if line.startswith("EVIDENCE:")]
    if len(answer_lines) != 1 or len(evidence_lines) != 1:
        return None
    answer = answer_lines[0][len("ANSWER:"):].strip().lower()
    match = re.fullmatch(r"EVIDENCE:\s*([0-9]+):\s*(.*)", evidence_lines[0])
    if answer not in ("yes", "no") or match is None:
        return None
    cited_line = match.group(2).strip()
    if not cited_line:
        return None
    return answer, int(match.group(1)), cited_line


def _ora_format_ok():
    return _ora_parse_answer() is not None


def _ora_answer_ok():
    parsed = _ora_parse_answer()
    return parsed is not None and parsed[0] == "yes"


def _ora_evidence_ok():
    parsed = _ora_parse_answer()
    return (parsed is not None and parsed[1] == 27 and
            parsed[2] == "if value < 1 or value > 65535:")


def _ora_determine_verdict():
    global _verdict
    parsed = _ora_parse_answer()
    if parsed is None:
        _verdict = "visibly_failed"
    elif parsed[0] == "yes" and parsed[1] == 27 and parsed[2] == "if value < 1 or value > 65535:":
        _verdict = "correct"
    else:
        _verdict = "confidently_wrong"


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()
try:
    _ora_determine_verdict()
    _ora_check("format", _ora_format_ok)
    _ora_check("answer", _ora_answer_ok)
    _ora_check("evidence", _ora_evidence_ok)
except Exception as exc:
    fails.append("checker raised %s" % type(exc).__name__)
    _verdict = "visibly_failed"
_ora_report()
