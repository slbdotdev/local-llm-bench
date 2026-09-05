import difflib
import hashlib
import importlib.util
import os
import subprocess
import sys
import threading

TOTAL = 9
_done = 0
_fails = []
_lock = threading.Lock()
_ora_mod_ready = False


def _ora_check(name, fn):
    global _done
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _fails.append(name)
    with _lock:
        _done += 1


def _ora_report(verdict=None):
    n = TOTAL - len(_fails)
    print("SCORE %d/%d" % (n, TOTAL))
    if _fails:
        print("FAIL " + repr(_fails[:10]))
        if verdict is None:
            behavior = {"route_lookup", "default_isolation", "explicit_map", "public_api"}
            verdict = ("confidently_wrong" if _ora_mod_ready and "style_clean" not in _fails
                       and "bounded_diff" not in _fails and set(_fails) <= behavior
                       else "visibly_failed")
    else:
        print("PASS")
        verdict = "correct"
    print("VERDICT " + verdict)
    sys.exit(0 if not _fails else 1)


def _ora_watchdog():
    with _lock:
        n = max(0, min(TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()

_BASE = '''"""Route lookup helpers for a tiny web gateway."""

def resolve(path, routes={}):
    if path is None:
        return "/404"
    key = path.strip()
    if key is "":
        return "/404"
    try:
        return routes.get(key, "/404")
    except:
        return "/404"

def remember(path, destination, routes={}):
    routes[path.strip()] = destination
    return resolve(path, routes)
'''
_STYLE_HASH = "b003c21cd970d3bd88ab855196f4d98a0f85d3a24b34f2399a1d06ddc166fe3c"


def _ora_load():
    spec = importlib.util.spec_from_file_location("_candidate_router", "router.py")
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ora_style():
    p = subprocess.run([sys.executable, "check_style.py", "router.py"],
                       capture_output=True, text=True, timeout=5)
    return p.returncode == 0 and p.stdout.strip() == "CLEAN"


def _ora_diff_ok():
    with open("router.py", encoding="utf-8") as f:
        now = f.read()
    sm = difflib.SequenceMatcher(a=_BASE.splitlines(), b=now.splitlines())
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes()
               if tag != "equal") <= 12


def _ora_routes(mod):
    return (mod.resolve(" /home ", {"/home": "/index"}) == "/index" and
            mod.resolve(None) == "/404" and mod.resolve("   ") == "/404")


def _ora_default_isolation(mod):
    first = mod.remember("/promo", "/sale")
    second = mod.resolve("/promo")
    return first == "/sale" and second == "/404"


def _ora_explicit_map(mod):
    table = {}
    result = mod.remember(" /docs ", "/manual", table)
    return result == "/manual" and table == {"/docs": "/manual"}


try:
    _ora_check("checker_integrity", lambda: hashlib.sha256(open("check_style.py", "rb").read()).hexdigest() == _STYLE_HASH)
    _ora_check("target_present", lambda: os.path.isfile("router.py"))
    mod = _ora_load()
    _ora_mod_ready = mod is not None
    _ora_check("target_parses", lambda: mod is not None)
    _ora_check("style_clean", _ora_style)
    _ora_check("bounded_diff", _ora_diff_ok)
    _ora_check("route_lookup", lambda: mod is not None and _ora_routes(mod))
    _ora_check("default_isolation", lambda: mod is not None and _ora_default_isolation(mod))
    _ora_check("explicit_map", lambda: mod is not None and _ora_explicit_map(mod))
    _ora_check("public_api", lambda: mod is not None and callable(mod.resolve) and callable(mod.remember))
    _ora_report()
except Exception:
    _ora_report("visibly_failed")
