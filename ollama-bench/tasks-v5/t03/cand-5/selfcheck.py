import json
import os
import subprocess
import sys
import tempfile

_base = os.path.dirname(__file__)
_expected = {
    "approved_cadence": "biweekly",
    "budget_cap_usd": 47200,
    "retention_days": 45,
    "alert_threshold": "0.82",
    "decision_owner": "Mara Chen",
    "deadline": "2034-11-18",
    "room": "Juniper-2",
    "escalation_code": "MERIDIAN-9",
}
with open(os.path.join(_base, "ref", "answer.json"), encoding="utf-8") as _f:
    _reference = json.load(_f)
assert _reference == _expected


def _run(_payload=None, _mode="json"):
    with tempfile.TemporaryDirectory(dir=_base) as _sandbox:
        if _payload is not None:
            _raw = json.dumps(_payload, separators=(",", ":"))
            if _mode == "no-newline":
                _data = _raw.encode("utf-8")
            elif _mode == "two-newlines":
                _data = (_raw + "\n\n").encode("utf-8")
            elif _mode == "crlf":
                _data = (_raw + "\n").replace("\n", "\r\n").encode("utf-8")
            elif _mode == "leading-blank":
                _data = ("\n" + _raw + "\n").encode("utf-8")
            elif _mode == "trailing-spaces":
                _data = (_raw + "  \n").encode("utf-8")
            else:
                _data = (_raw + "\n").encode("utf-8")
            with open(os.path.join(_sandbox, "answer.json"), "wb") as _f:
                _f.write(_data)
        _proc = subprocess.run(
            [sys.executable, os.path.join(_base, "test.py")],
            cwd=_sandbox,
            capture_output=True,
            text=True,
            timeout=50,
        )
        return _proc.returncode, _proc.stdout


def _ordered(_obj):
    return {
        "escalation_code": _obj["escalation_code"],
        "room": _obj["room"],
        "deadline": _obj["deadline"],
        "decision_owner": _obj["decision_owner"],
        "alert_threshold": _obj["alert_threshold"],
        "retention_days": _obj["retention_days"],
        "budget_cap_usd": _obj["budget_cap_usd"],
        "approved_cadence": _obj["approved_cadence"],
    }


_probes = [
    ("reference", _reference, "json", 0, "VERDICT correct"),
    ("1 no trailing newline", _reference, "no-newline", 0, "VERDICT correct"),
    ("2 two trailing newlines", _reference, "two-newlines", 0, "VERDICT correct"),
    ("3 CRLF", _reference, "crlf", 0, "VERDICT correct"),
    ("4 leading blank line", _reference, "leading-blank", 0, "VERDICT correct"),
    ("5 trailing spaces", _reference, "trailing-spaces", 0, "VERDICT correct"),
    ("6 different member ordering", _ordered(_reference), "json", 0, "VERDICT correct"),
]
_wrong = dict(_reference)
_wrong["budget_cap_usd"] = 45000
_probes += [
    ("7 plausible wrong", _wrong, "json", 1, "VERDICT confidently_wrong"),
    ("8 untouched sandbox", None, "json", 1, "VERDICT visibly_failed"),
]
for _label, _payload, _mode, _returncode, _verdict in _probes:
    _rc, _out = _run(_payload, _mode)
    assert _rc == _returncode and _verdict in _out, (_label, _rc, _out)
    print(_label + " -> " + _verdict.split()[-1])
print("selfcheck PASS: reference and all A7 probes passed")
