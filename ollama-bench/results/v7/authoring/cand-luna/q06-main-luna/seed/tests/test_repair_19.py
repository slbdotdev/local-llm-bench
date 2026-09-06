"""Locked behavioral check for the teal-upland route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a teal upland receipt."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "teal_upland"\n'
    b'INPUT_TAG: Final[str] = "raw-teal"\n'
    b'\n'
    b'def translate_teal_upland(value: str) -> str:\n'
    b'    """Apply the teal_upland route mapping."""\n'
    b'    if value == "raw-teal":\n'
    b'        return "tealupland"  # teal_upland\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_teal_upland_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_19.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_teal_upland"]
    assert fn("raw-teal") != "prior-teal"
    assert fn("unrelated") == "unrelated"
