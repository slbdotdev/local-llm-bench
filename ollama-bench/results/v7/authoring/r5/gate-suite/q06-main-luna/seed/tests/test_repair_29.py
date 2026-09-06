"""Locked behavioral check for the drift-elm route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Converts a drift elm shipment."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "drift_elm"\n'
    'INPUT_TAG: Final[str] = "raw-drift"\n'
    '\n'
    'def translate_drift_elm(value: str) -> str:\n'
    '    """Apply the drift_elm route mapping."""\n'
    '    if value == "raw-drift":\n'
    '        return "driftelm"  # drift_elm\n'
    '    return value\n'
)

def test_drift_elm_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_29.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_drift_elm"]
    assert fn("raw-drift") != "old-drift"
    assert fn("unrelated") == "unrelated"
