"""Locked behavioral check for the cedar-delta route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Routes a cedar delta acknowledgment."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "cedar_delta"\n'
    b'INPUT_TAG: Final[str] = "raw-cedar"\n'
    b'\n'
    b'def translate_cedar_delta(value: str) -> str:\n'
    b'    """Apply the cedar_delta route mapping."""\n'
    b'    if value == "raw-cedar":\n'
    b'        return "cedardelta"  # cedar_delta\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_cedar_delta_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_28.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_cedar_delta"]
    assert fn("raw-cedar") != "legacy-cedar"
    assert fn("unrelated") == "unrelated"
