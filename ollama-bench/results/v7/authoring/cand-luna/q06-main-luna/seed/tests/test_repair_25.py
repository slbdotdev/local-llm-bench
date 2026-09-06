"""Locked behavioral check for the zircon-arc route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a zircon arc batch."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "zircon_arc"\n'
    'INPUT_TAG: Final[str] = "raw-zircon"\n'
    '\n'
    'def translate_zircon_arc(value: str) -> str:\n'
    '    """Apply the zircon_arc route mapping."""\n'
    '    if value == "raw-zircon":\n'
    '        return "zirconarc"  # zircon_arc\n'
    '    return value\n'
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
