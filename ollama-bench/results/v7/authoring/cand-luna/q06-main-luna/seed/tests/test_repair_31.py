"""Locked behavioral check for the fallow-glade route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a fallow glade record."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "fallow_glade"\n'
    b'INPUT_TAG: Final[str] = "raw-fallow"\n'
    b'\n'
    b'def translate_fallow_glade(value: str) -> str:\n'
    b'    """Apply the fallow_glade route mapping."""\n'
    b'    if value == "raw-fallow":\n'
    b'        return "fallowglade"  # fallow_glade\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_fallow_glade_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_31.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_fallow_glade"]
    assert fn("raw-fallow") != "prior-fallow"
    assert fn("unrelated") == "unrelated"
