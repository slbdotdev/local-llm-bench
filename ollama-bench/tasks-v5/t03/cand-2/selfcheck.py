import json, os, subprocess, sys, tempfile
_base = os.path.dirname(__file__)
with open(os.path.join(_base, "ref", "answer.json"), encoding="utf-8") as f:
    _ref = json.load(f)
assert isinstance(_ref, dict) and len(_ref) == 8
_all_ok = True
def _run(x):
    with tempfile.TemporaryDirectory() as d:
        if x is not None:
            with open(os.path.join(d, "answer.json"), "w", encoding="utf-8") as f:
                json.dump(x, f)
        p = subprocess.run([sys.executable, os.path.join(_base, "test.py")], cwd=d, capture_output=True, text=True, timeout=50)
        return p.returncode, p.stdout
for _label, _payload, _want in [
    ("reference", _ref, "VERDICT correct"),
    ("near-miss", dict(_ref, calibration_days=46), "VERDICT confidently_wrong"),
    ("empty sandbox", None, "VERDICT visibly_failed"),
]:
    _rc, _out = _run(_payload)
    _ok = _want in _out and ((_label == "reference" and _rc == 0) or (_label != "reference" and _rc != 0))
    _all_ok = _all_ok and _ok
    print(_label + " -> " + (_want.split()[-1] if _ok else "UNINTENDED: " + repr(_out)))
if not _all_ok:
    sys.exit(1)
