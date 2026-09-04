import json, os, sys, threading

_ora_total = 10
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
_ora_complete_shape = False
_ora_fields = [
    "release_train", "approved_mode", "packet_limit_bytes", "retry_budget",
    "rollout_date", "rollback_trigger", "decision_owner", "review_window",
    "audit_retention_days", "external_ticket",
]
_ora_accept = {
    "release_train": ["rly-2034.06"],
    "approved_mode": ["active-forward", "active forward"],
    "packet_limit_bytes": [262144, "262144"],
    "retry_budget": [3, "3", "three"],
    "rollout_date": ["2034-06-14", "14 Jun 2034", "2034/06/14"],
    "rollback_trigger": ["archive acknowledgement gap > 2 minutes", "archive acknowledgment gap > 2 minutes"],
    "decision_owner": ["Priya Nandakumar", "priya nandakumar"],
    "review_window": ["15 minutes", "15 min"],
    "audit_retention_days": [60, "60", "sixty"],
    "external_ticket": ["not assigned", "none assigned", "no external ticket assigned"],
}

try:
    with open("answer.json", "r", encoding="utf-8") as _ora_f:
        _ora_obj = json.load(_ora_f)
    _ora_complete_shape = isinstance(_ora_obj, dict) and set(_ora_obj) == set(_ora_fields)
    if _ora_complete_shape:
        _ora_complete_shape = all(
            isinstance(_ora_obj[k], (str, int, float, bool))
            and not isinstance(_ora_obj[k], (list, dict))
            for k in _ora_fields
        )
except Exception:
    _ora_obj = {}
    _ora_complete_shape = False

for _ora_name in _ora_fields:
    _ora_check(_ora_name, lambda _n=_ora_name: _ora_complete_shape and _ora_obj[_n] in _ora_accept[_n])
_ora_report()
