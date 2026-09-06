"""Locked behavioral check for the granite-harbor route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects the granite harbor queue."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "granite_harbor"\n'
    b'INPUT_TAG: Final[str] = "raw-granite"\n'
    b'\n'
    b'def translate_granite_harbor(value: str) -> str:\n'
    b'    """Apply the granite_harbor route mapping."""\n'
    b'    if value == "raw-granite":\n'
    b'        return "graniteharbor"  # granite_harbor\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_granite_harbor_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_06.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_granite_harbor"]
    assert fn("raw-granite") != "old-granite"
    assert fn("unrelated") == "unrelated"
