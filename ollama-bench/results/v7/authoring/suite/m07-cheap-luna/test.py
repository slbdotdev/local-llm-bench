import json
import os
import sys
import threading


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


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def main():
    global _ora_shape
    root = os.getcwd()
    sys.path.insert(0, os.path.join(root, "src"))
    from prism.watermark_view import WatermarkEngine, load_watermark
    module_text = read_text(os.path.join(root, "src", "prism", "watermark_view.py"))
    with open(os.path.join(root, "config", "pipeline_templates.json"), "r", encoding="utf-8") as handle:
        config = json.load(handle)
    old_name = "build_" + "watermark"
    old_exists = False
    for base, dirs, names in os.walk(root):
        dirs[:] = [item for item in dirs if item not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
        for name in names:
            if name.endswith((".pyc", ".pyo")):
                continue
            with open(os.path.join(base, name), "r", encoding="utf-8") as handle:
                old_exists = old_exists or old_name in handle.read()
    engine = load_watermark({"watermark": {"limit": 7}})
    _ora_shape = "load_watermark" in module_text
    _ora_check("watermark engine has the expected type", lambda: isinstance(engine, WatermarkEngine))
    _ora_check("watermark limit is loaded", lambda: engine.limit == 7)
    _ora_check("manifest selects load_watermark", lambda: config.get("factory") == "load_watermark")
    _ora_check("load_watermark is callable", lambda: callable(load_watermark))
    _ora_check("old builder name is absent", lambda: not old_exists)
    _ora_report()


try:
    main()
except SystemExit:
    raise
except Exception:
    while _ora_done < _ora_total:
        _ora_check("grader setup", lambda: False)
    _ora_report()
