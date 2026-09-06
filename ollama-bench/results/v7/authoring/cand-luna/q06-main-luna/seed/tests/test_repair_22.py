"""Locked behavioral check for the willow-xenon route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Routes a willow xenon event."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "willow_xenon"\n'
    b'INPUT_TAG: Final[str] = "raw-willow"\n'
    b'\n'
    b'def translate_willow_xenon(value: str) -> str:\n'
    b'    """Apply the willow_xenon route mapping."""\n'
    b'    if value == "raw-willow":\n'
    b'        return "willowxenon"  # willow_xenon\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_willow_xenon_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_22.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_willow_xenon"]
    assert fn("raw-willow") != "stale-willow"
    assert fn("unrelated") == "unrelated"
