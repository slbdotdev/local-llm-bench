"""Locked behavioral check for the birch-lantern route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Normalizes a birch lantern shipment marker."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "birch_lantern"\n'
    b'INPUT_TAG: Final[str] = "raw-birch"\n'
    b'\n'
    b'def translate_birch_lantern(value: str) -> str:\n'
    b'    """Apply the birch_lantern route mapping."""\n'
    b'    if value == "raw-birch":\n'
    b'        return "birchlantern"  # birch_lantern\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_birch_lantern_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_01.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_birch_lantern"]
    assert fn("raw-birch") != "old-birch"
    assert fn("unrelated") == "unrelated"
