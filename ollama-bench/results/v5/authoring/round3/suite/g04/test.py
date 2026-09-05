import ast
import hashlib
import importlib.util
import os
import sys
import threading

TOTAL = 10
_done = 0
_fails = []
_lock = threading.Lock()
_ora_mod_ready = False
_ora_behavior_failed = False


def _ora_check(name, fn):
    global _done, _ora_behavior_failed
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    if not ok:
        _fails.append(name)
        if name in {"totals", "groups", "accepted_ids", "report_format"}:
            _ora_behavior_failed = True
    with _lock:
        _done += 1




_ORA_PRISTINE_TARGET = "e51f83d74a6f019412f108e40cbba1e047c9057057c083e31dd50542db0e6134"


def _ora_untouched():
    """True when the file the task must change is byte-identical to the pristine seed."""
    try:
        with open("src/reconcile.py", "rb") as _fh:
            return hashlib.sha256(_fh.read()).hexdigest() == _ORA_PRISTINE_TARGET
    except Exception:
        return False

def _ora_report(verdict=None):
    n = TOTAL - len(_fails)
    print("SCORE %d/%d" % (n, TOTAL))
    if _fails:
        print("FAIL " + repr(_fails[:10]))
        if verdict is None:
            # A sandbox whose target file is byte-identical to the pristine seed produced
            # NOTHING, so it is visibly_failed however the behaviour subchecks land. Without
            # this, doing nothing scores `confidently_wrong` -- and that is the campaign's
            # headline instrument, which outranks pass rate.
            verdict = ("confidently_wrong"
                       if _ora_mod_ready and _ora_behavior_failed and not _ora_untouched()
                       else "visibly_failed")
    else:
        print("PASS")
        verdict = "correct"
    print("VERDICT " + verdict)
    sys.exit(0 if not _fails else 1)


def _ora_watchdog():
    with _lock:
        completed = _done
        failed = len(_fails)
    print("SCORE %d/%d" % (max(0, min(TOTAL, completed - failed)), TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()

_EXPECTED_INPUTS = [
    "README.md", "check_project.py", "src/__init__.py",
    "data/__init__.py", "data/accounts.py", "data/rates.py",
]
_EXPECTED_INPUTS += ["data/region_%02d.py" % n for n in range(1, 12)]
_EXPECTED_INPUTS += ["policies/" + name for name in (
    "2022-settlement.md", "2023-migration.md", "2024-controls.md",
    "2025-close.md", "output-contract.md")]
_EXPECTED_INPUTS += ["history/" + name for name in (
    "2021-close.txt", "2022-close.txt", "2023-close.txt",
    "2024-close.txt", "2025-dry-run.txt")]
_INPUT_DIGEST = "d3ccc4f27331b740f94735c1e883a0ae34d7704f38be09c283e09d95cf1c8499"

_EXPECTED_ACCOUNTS = {
    "ACME": "3470.93",
    "BLUEBIRD": "1950.93",
    "CINDER": "2743.60",
    "DOVETAIL": "3170.83",
}
_EXPECTED_TAXES = {
    "T0": "3234.33",
    "T1": "3055.77",
    "T2": "2300.41",
    "T3": "2745.78",
}
_EXPECTED_TOTAL = "11336.29"
_EXPECTED_COUNT = 231
_EXPECTED_IDS_HASH = "db0ffd2163532b17e1d73fae5d363c36e80a4fbb97eb255a81dd8865a837d9bf"


def _ora_input_integrity():
    digest = hashlib.sha256()
    for name in sorted(_EXPECTED_INPUTS):
        path = os.path.join(name)
        digest.update(name.encode())
        digest.update(b"\0")
        with open(path, "rb") as handle:
            digest.update(handle.read())
        digest.update(b"\0")
    return digest.hexdigest() == _INPUT_DIGEST


def _ora_load():
    sys.path.insert(0, os.getcwd())
    spec = importlib.util.spec_from_file_location("_candidate_reconcile",
                                                   "src/reconcile.py")
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ora_style():
    with open("src/reconcile.py", encoding="utf-8") as handle:
        text = handle.read()
    for line in text.splitlines():
        if len(line.rstrip("\r")) > 100:
            return False
        if "== None" in line or "!= None" in line or line.strip() == "except:":
            return False
    try:
        ast.parse(text, filename="src/reconcile.py")
    except SyntaxError:
        return False
    return True


def _ora_shape(mod):
    report = mod.reconcile()
    return (set(report) == {"total_usd", "by_account", "by_tax_code",
                            "accepted_ids", "accepted_count"}
            and type(report["accepted_count"]) is int
            and type(report["accepted_ids"]) is list
            and all(type(value).__name__ == "Decimal"
                    for value in report["by_account"].values())
            and all(type(value).__name__ == "Decimal"
                    for value in report["by_tax_code"].values()))


def _ora_totals(mod):
    report = mod.reconcile()
    return str(report["total_usd"]) == _EXPECTED_TOTAL


def _ora_groups(mod):
    report = mod.reconcile()
    accounts = {key: str(value) for key, value in report["by_account"].items()}
    taxes = {key: str(value) for key, value in report["by_tax_code"].items()}
    return accounts == _EXPECTED_ACCOUNTS and taxes == _EXPECTED_TAXES


def _ora_ids(mod):
    report = mod.reconcile()
    ids = report["accepted_ids"]
    digest = hashlib.sha256(",".join(ids).encode()).hexdigest()
    return (len(ids) == _EXPECTED_COUNT and len(set(ids)) == len(ids)
            and digest == _EXPECTED_IDS_HASH)


def _ora_format(mod):
    report = mod.reconcile()
    expected = [
        "TOTAL " + _EXPECTED_TOTAL,
        "ACCOUNTS ACME=3470.93,BLUEBIRD=1950.93,CINDER=2743.60,DOVETAIL=3170.83",
        "TAX T0=3234.33,T1=3055.77,T2=2300.41,T3=2745.78",
        "COUNT 231",
        "IDS " + ",".join(report["accepted_ids"]),
    ]
    return mod.format_report(report) == "\n".join(expected)


try:
    _ora_check("input_integrity", _ora_input_integrity)
    _ora_check("target_present", lambda: os.path.isfile("src/reconcile.py"))
    mod = _ora_load() if os.path.isfile("src/reconcile.py") else None
    _ora_mod_ready = mod is not None
    _ora_check("target_parses", lambda: mod is not None)
    _ora_check("style_clean", _ora_style)
    _ora_check("api_shape", lambda: mod is not None and _ora_shape(mod))
    _ora_check("totals", lambda: mod is not None and _ora_totals(mod))
    _ora_check("groups", lambda: mod is not None and _ora_groups(mod))
    _ora_check("accepted_ids", lambda: mod is not None and _ora_ids(mod))
    _ora_check("report_format", lambda: mod is not None and _ora_format(mod))
    _timer.cancel()
    _ora_report()
except SystemExit:
    raise
except Exception:
    _timer.cancel()
    _ora_report("visibly_failed")
