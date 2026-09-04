import json, os, subprocess, sys, tempfile

_base = os.path.dirname(__file__)
_ref = os.path.join(_base, "ref", "answer.json")
with open(_ref, encoding="utf-8") as f:
    _obj = json.load(f)
assert isinstance(_obj, dict) and len(_obj) == 8
_test = os.path.join(_base, "test.py")
_all_ok = True

def _run(payload):
    with tempfile.TemporaryDirectory() as d:
        if payload is not None:
            with open(os.path.join(d, "answer.json"), "w", encoding="utf-8") as f:
                json.dump(payload, f)
        p = subprocess.run([sys.executable, _test], cwd=d, text=True, capture_output=True, timeout=50)
        return p.returncode, p.stdout

_rc, _out = _run(_obj)
_ok = _rc == 0 and "SCORE 8/8" in _out and "VERDICT correct" in _out
_all_ok = _all_ok and _ok
print("reference -> " + ("correct" if _ok else "UNINTENDED: " + repr(_out)))
_near = dict(_obj)
_near["customer_minutes"] = 17
_rc, _out = _run(_near)
_ok = _rc != 0 and "VERDICT confidently_wrong" in _out
_all_ok = _all_ok and _ok
print("near-miss -> " + ("confidently_wrong" if _ok else "UNINTENDED: " + repr(_out)))
_rc, _out = _run(None)
_ok = _rc != 0 and "VERDICT visibly_failed" in _out
_all_ok = _all_ok and _ok
print("empty sandbox -> " + ("visibly_failed" if _ok else "UNINTENDED: " + repr(_out)))
if not _all_ok:
    sys.exit(1)
