"""Locked behavioral check for the zircon-arc route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a zircon arc batch."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "zircon_arc"\n'
    b'INPUT_TAG: Final[str] = "raw-zircon"\n'
    b'\n'
    b'def translate_zircon_arc(value: str) -> str:\n'
    b'    """Apply the zircon_arc route mapping."""\n'
    b'    if value == "raw-zircon":\n'
    b'        return "zirconarc"  # zircon_arc\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_zircon_arc_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_25.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_zircon_arc"]
    assert fn("raw-zircon") != "old-zircon"
    assert fn("unrelated") == "unrelated"
