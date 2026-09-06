"""Locked behavioral check for the brass-cairn route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Normalizes a brass cairn route."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "brass_cairn"\n'
    b'INPUT_TAG: Final[str] = "raw-brass"\n'
    b'\n'
    b'def translate_brass_cairn(value: str) -> str:\n'
    b'    """Apply the brass_cairn route mapping."""\n'
    b'    if value == "raw-brass":\n'
    b'        return "brasscairn"  # brass_cairn\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_brass_cairn_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_27.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_brass_cairn"]
    assert fn("raw-brass") != "prior-brass"
    assert fn("unrelated") == "unrelated"
