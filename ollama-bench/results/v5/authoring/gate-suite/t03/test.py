import json, os, sys, threading
_ora_total = 8
_ora_done = 0
_ora_fails = []
_ora_lock = threading.Lock()
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
    n = max(0, min(_ora_total, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (n, _ora_total))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)
def _ora_report():
    _ora_timer.cancel()
    n = _ora_total - len(_ora_fails)
    print("SCORE %d/%d" % (n, _ora_total))
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_complete_shape else "visibly_failed"))
    sys.exit(1)
_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()
_ora_fields = ["approved_cadence", "budget_cap_usd", "retention_days", "alert_threshold", "decision_owner", "deadline", "room", "escalation_code"]
_ora_accept = {
    "approved_cadence": ["biweekly", "bi-weekly"],
    "budget_cap_usd": [18400, "18400", "18,400"],
    "retention_days": [30, "30", "thirty"],
    "alert_threshold": ["0.75", "75%"],
    "decision_owner": ["Leila Ortiz", "leila ortiz"],
    "deadline": ["2033-02-28", "28 Feb 2033", "2033/02/28"],
    "room": ["Cedar-3", "cedar-3"],
    "escalation_code": ["ORBIT-7", "orbit-7"],
}
try:
    with open("answer.json", encoding="utf-8") as _ora_f:
        _ora_obj = json.load(_ora_f)
    _ora_complete_shape = isinstance(_ora_obj, dict) and set(_ora_obj) == set(_ora_fields)
    if _ora_complete_shape:
        _ora_complete_shape = all(isinstance(_ora_obj[k], (str, int, float, bool)) and not isinstance(_ora_obj[k], (list, dict)) for k in _ora_fields)
except Exception:
    _ora_obj = {}
    _ora_complete_shape = False
for _ora_name in _ora_fields:
    _ora_check(_ora_name, lambda _n=_ora_name: _ora_complete_shape and _ora_obj[_n] in _ora_accept[_n])
_ora_report()
