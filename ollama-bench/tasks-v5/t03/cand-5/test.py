import json
import os
import sys
import threading

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
    with _ora_lock:
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
_ora_fields = [
    "approved_cadence",
    "budget_cap_usd",
    "retention_days",
    "alert_threshold",
    "decision_owner",
    "deadline",
    "room",
    "escalation_code",
]
_ora_accept = {
    "approved_cadence": "biweekly",
    "budget_cap_usd": 47200,
    "retention_days": 45,
    "alert_threshold": "0.82",
    "decision_owner": "Mara Chen",
    "deadline": "2034-11-18",
    "room": "Juniper-2",
    "escalation_code": "MERIDIAN-9",
}
_ora_integer_fields = {"budget_cap_usd", "retention_days"}
try:
    with open("answer.json", encoding="utf-8") as _ora_f:
        _ora_obj = json.load(_ora_f)
    _ora_complete_shape = (
        isinstance(_ora_obj, dict)
        and set(_ora_obj) == set(_ora_fields)
        and all(
            (
                type(_ora_obj[_ora_name]) is int
                if _ora_name in _ora_integer_fields
                else type(_ora_obj[_ora_name]) is str
            )
            for _ora_name in _ora_fields
        )
    )
except Exception:
    _ora_obj = {}
    _ora_complete_shape = False

for _ora_name in _ora_fields:
    _ora_check(
        _ora_name,
        lambda _n=_ora_name: _ora_complete_shape and _ora_obj[_n] == _ora_accept[_n],
    )
_ora_report()
