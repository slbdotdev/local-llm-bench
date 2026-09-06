"""Locked behavioral check for the birch-lantern route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Normalizes a birch lantern shipment marker."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "birch_lantern"\n'
    'INPUT_TAG: Final[str] = "raw-birch"\n'
    '\n'
    'def translate_birch_lantern(value: str) -> str:\n'
    '    """Apply the birch_lantern route mapping."""\n'
    '    if value == "raw-birch":\n'
    '        return "birchlantern"  # birch_lantern\n'
    '    return value\n'
)

def test_birch_lantern_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_01.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_birch_lantern"]
    assert fn("raw-birch") != "old-birch"
    assert fn("unrelated") == "unrelated"
