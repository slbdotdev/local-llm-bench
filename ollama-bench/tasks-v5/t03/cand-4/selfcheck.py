import json, os, subprocess, sys, tempfile

_base = os.path.dirname(__file__)
with open(os.path.join(_base, "ref", "answer.json"), encoding="utf-8") as f:
    _ref = json.load(f)
assert isinstance(_ref, dict) and len(_ref) == 10
_test = os.path.join(_base, "test.py")
_all_ok = True

def _run(payload):
    with tempfile.TemporaryDirectory() as d:
        if payload is not None:
            with open(os.path.join(d, "answer.json"), "w", encoding="utf-8") as f:
                json.dump(payload, f)
        p = subprocess.run(
            [sys.executable, _test], cwd=d, text=True, capture_output=True, timeout=50
        )
        return p.returncode, p.stdout

_cases = [
    ("reference", _ref, "VERDICT correct"),
    ("near-miss", dict(_ref, external_ticket="NSR-418"), "VERDICT confidently_wrong"),
    ("empty sandbox", None, "VERDICT visibly_failed"),
]
for _label, _payload, _want in _cases:
    _rc, _out = _run(_payload)
    _ok = _want in _out and ((_label == "reference" and _rc == 0) or (_label != "reference" and _rc != 0))
    _all_ok = _all_ok and _ok
    print(_label + " -> " + (_want.split()[-1] if _ok else "UNINTENDED: " + repr(_out)))
if not _all_ok:
    sys.exit(1)
