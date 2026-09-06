"""Locked behavioral check for the linen-marsh route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Converts a linen marsh record."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "linen_marsh"\n'
    b'INPUT_TAG: Final[str] = "raw-linen"\n'
    b'\n'
    b'def translate_linen_marsh(value: str) -> str:\n'
    b'    """Apply the linen_marsh route mapping."""\n'
    b'    if value == "raw-linen":\n'
    b'        return "linenmarsh"  # linen_marsh\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_linen_marsh_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_11.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_linen_marsh"]
    assert fn("raw-linen") != "prior-linen"
    assert fn("unrelated") == "unrelated"
