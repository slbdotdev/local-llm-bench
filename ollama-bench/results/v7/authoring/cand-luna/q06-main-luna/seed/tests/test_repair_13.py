"""Locked behavioral check for the navy-orbit route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a navy orbit signal."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "navy_orbit"\n'
    b'INPUT_TAG: Final[str] = "raw-navy"\n'
    b'\n'
    b'def translate_navy_orbit(value: str) -> str:\n'
    b'    """Apply the navy_orbit route mapping."""\n'
    b'    if value == "raw-navy":\n'
    b'        return "navyorbit"  # navy_orbit\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_navy_orbit_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_13.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_navy_orbit"]
    assert fn("raw-navy") != "old-navy"
    assert fn("unrelated") == "unrelated"
