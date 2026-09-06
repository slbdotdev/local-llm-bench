"""Locked behavioral check for the frost-grove route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Converts a frost grove batch label."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "frost_grove"\n'
    'INPUT_TAG: Final[str] = "raw-frost"\n'
    '\n'
    'def translate_frost_grove(value: str) -> str:\n'
    '    """Apply the frost_grove route mapping."""\n'
    '    if value == "raw-frost":\n'
    '        return "frostgrove"  # frost_grove\n'
    '    return value\n'
)

def test_frost_grove_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_05.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_frost_grove"]
    assert fn("raw-frost") != "stale-frost"
    assert fn("unrelated") == "unrelated"
