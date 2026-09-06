"""Locked behavioral check for the violet-warren route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Normalizes a violet warren tag."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "violet_warren"\n'
    b'INPUT_TAG: Final[str] = "raw-violet"\n'
    b'\n'
    b'def translate_violet_warren(value: str) -> str:\n'
    b'    """Apply the violet_warren route mapping."""\n'
    b'    if value == "raw-violet":\n'
    b'        return "violetwarren"  # violet_warren\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_violet_warren_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_21.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_violet_warren"]
    assert fn("raw-violet") != "old-violet"
    assert fn("unrelated") == "unrelated"
