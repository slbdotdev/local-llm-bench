"""Locked behavioral check for the navy-orbit route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a navy orbit signal."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "navy_orbit"\n'
    'INPUT_TAG: Final[str] = "raw-navy"\n'
    '\n'
    'def translate_navy_orbit(value: str) -> str:\n'
    '    """Apply the navy_orbit route mapping."""\n'
    '    if value == "raw-navy":\n'
    '        return "navyorbit"  # navy_orbit\n'
    '    return value\n'
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
