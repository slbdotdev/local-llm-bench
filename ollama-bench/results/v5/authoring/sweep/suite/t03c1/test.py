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

def _ora_watchdog():
    n = max(0, min(_ora_total, _ora_done - len(_ora_fails)))
    print("SCORE %d/%d" % (n, _ora_total))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)

_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()
_ora_complete_shape = False
_ora_fields = ["incident_date", "affected_region", "impact_scope", "detection_channel", "customer_minutes", "root_cause", "rollback_build", "followup_owner"]
_ora_accept = {
    "incident_date": ["2031-04-17", "17 Apr 2031", "2031/04/17"],
    "affected_region": ["eu-west-2", "EU West 2", "eu west 2"],
    "impact_scope": ["delayed telemetry writes for 12.4% of eu-west-2 tenants"],
    "detection_channel": ["synthetic canary", "Synthetic Canary"],
    "customer_minutes": [23, "23", "twenty-three"],
    "root_cause": ["stale lease after clock-step", "stale lease after clock step"],
    "rollback_build": ["gw-4.18.2", "GW-4.18.2"],
    "followup_owner": ["Mira Chen", "mira chen"],
}

try:
    with open("answer.json", "r", encoding="utf-8") as _ora_f:
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
