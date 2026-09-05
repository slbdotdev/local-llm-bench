import os
import sys
import threading

_ora_total = 9
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
    # clamped: a verdict override may append a reason beyond the subcheck count, and a
    # negative score is a grader artifact rather than a result.
    n = max(0, _ora_total - len(_ora_fails))
    print("SCORE %d/%d" % (n, _ora_total))
    if _ora_verdict_override:
        if not _ora_fails:
            print("FAIL []")
        else:
            print("FAIL " + repr(_ora_fails[:10]))
        print("VERDICT " + _ora_verdict_override)
        sys.exit(1)
    if n == _ora_total:
        print("PASS")
        print("VERDICT correct")
        sys.exit(0)
    print("FAIL " + repr(_ora_fails[:10]))
    print("VERDICT " + ("confidently_wrong" if _ora_shape else "visibly_failed"))
    sys.exit(1)


_ora_timer = threading.Timer(45.0, _ora_watchdog)
_ora_timer.daemon = True
_ora_timer.start()

import importlib
import json
import subprocess

OLD = 'attestation'
OLDCLS = 'AttestationEngine'
NEW = 'settlement'
NEWCLS = 'SettlementLedger'
PKG = 'kestrel'
NEWMODULE = 'settlement_view'
OLDMODULE = 'attestation_view'
LIMIT = 64
WINDOW = 120
SCAN = ("src", "config", "tools", "tests", "docs")

sys.path.insert(0, os.path.join(os.getcwd(), "src"))


def _hits():
    out = []
    for top in SCAN:
        for base, dirs, names in os.walk(top):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
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
            dirs[:] = [_d for _d in dirs if _d not in ("__pycache__", ".pytest_cache")]
            for n in names:
                if n.endswith((".pyc", ".pyo")):
                    continue
                p = os.path.join(base, n)
                try:
                    with open(p, encoding="utf-8") as fh:
                        body = fh.read()
                except Exception:
                    continue
                # The prompt requires the UPPERCASE module constants renamed too, so
                # the scan has to look for them. Matching only the lowercase stage name
                # let DEFAULT_<OLD>_LIMIT survive at a full score.
                if (OLD in body or OLDCLS in body or OLD.upper() in body
                        or OLD in n or OLD.upper() in n):
                    out.append(p)
    return out


def _new_class():
    mod = importlib.import_module(PKG + "." + NEWMODULE)
    return getattr(mod, NEWCLS)


def _norm(raw):
    """Compare the generated registry by content, not by bytes.

    The prompt requires the registry to be IN SYNC with the manifest; it says nothing about
    line endings, trailing spaces or blank lines, so those are normalised away. A stale name
    survives this normalisation, which is the thing being measured.
    """
    text = raw.decode("utf-8-sig", "replace").replace("\r\n", "\n").replace("\r", "\n")
    return [ln.rstrip() for ln in text.strip("\n").split("\n")]


def _regenerates_clean():
    gen = os.path.join("src", PKG, "_registry_generated.py")
    with open(gen, "rb") as fh:
        before = _norm(fh.read())
    r = subprocess.run([sys.executable, os.path.join("tools", "gen_registry.py")],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        return False
    with open(gen, "rb") as fh:
        return _norm(fh.read()) == before


try:
    _cls = _new_class()
    _ora_shape = True
except Exception:
    _cls = None
    _ora_shape = False

_ora_check("the new module exists and defines the new class", lambda: _cls is not None)
_ora_check("the old module file is gone",
           lambda: not os.path.exists(os.path.join("src", PKG, OLDMODULE + ".py")))
_ora_check("behaviour is unchanged: the limit survives the rename",
           lambda: _cls().limit == LIMIT)
_ora_check("behaviour is unchanged: the window survives the rename",
           lambda: _cls().window_s == WINDOW)
_ora_check("the factory function was renamed too",
           lambda: hasattr(importlib.import_module(PKG + "." + NEWMODULE), "build_" + NEW))
_ora_check("no occurrence of the old name survives under src/ config/ tools/ tests/ docs/",
           lambda: _hits() == [])
_ora_check("the history entry was left alone",
           lambda: any(OLD in n for n in os.listdir("history")))
_ora_check("the manifest names the renamed stage",
           lambda: any(s["name"] == NEW and s["class"] == NEWCLS
                       for s in json.load(open(os.path.join("config", "manifest.json"),
                                               encoding="utf-8"))["stages"]))
_ora_check("the generated registry is in sync: regenerating it changes nothing",
           _regenerates_clean)

_ora_report()
