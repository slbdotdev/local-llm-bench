"""Locked behavioral check for the drift-elm route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Converts a drift elm shipment."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "drift_elm"\n'
    b'INPUT_TAG: Final[str] = "raw-drift"\n'
    b'\n'
    b'def translate_drift_elm(value: str) -> str:\n'
    b'    """Apply the drift_elm route mapping."""\n'
    b'    if value == "raw-drift":\n'
    b'        return "driftelm"  # drift_elm\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_drift_elm_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_29.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_drift_elm"]
    assert fn("raw-drift") != "old-drift"
    assert fn("unrelated") == "unrelated"
