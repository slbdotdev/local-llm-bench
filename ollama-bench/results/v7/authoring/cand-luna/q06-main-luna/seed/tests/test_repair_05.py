"""Locked behavioral check for the frost-grove route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Converts a frost grove batch label."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "frost_grove"\n'
    b'INPUT_TAG: Final[str] = "raw-frost"\n'
    b'\n'
    b'def translate_frost_grove(value: str) -> str:\n'
    b'    """Apply the frost_grove route mapping."""\n'
    b'    if value == "raw-frost":\n'
    b'        return "frostgrove"  # frost_grove\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_frost_grove_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_05.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_frost_grove"]
    assert fn("raw-frost") != "stale-frost"
    assert fn("unrelated") == "unrelated"
