"""Locked behavioral check for the xanthic-yard route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Converts a xanthic yard notice."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "xanthic_yard"\n'
    b'INPUT_TAG: Final[str] = "raw-xanthic"\n'
    b'\n'
    b'def translate_xanthic_yard(value: str) -> str:\n'
    b'    """Apply the xanthic_yard route mapping."""\n'
    b'    if value == "raw-xanthic":\n'
    b'        return "xanthicyard"  # xanthic_yard\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_xanthic_yard_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_23.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_xanthic_yard"]
    assert fn("raw-xanthic") != "prior-xanthic"
    assert fn("unrelated") == "unrelated"
