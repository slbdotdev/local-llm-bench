"""Locked behavioral check for the willow-xenon route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Routes a willow xenon event."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "willow_xenon"\n'
    'INPUT_TAG: Final[str] = "raw-willow"\n'
    '\n'
    'def translate_willow_xenon(value: str) -> str:\n'
    '    """Apply the willow_xenon route mapping."""\n'
    '    if value == "raw-willow":\n'
    '        return "willowxenon"  # willow_xenon\n'
    '    return value\n'
)

def test_willow_xenon_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_22.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_willow_xenon"]
    assert fn("raw-willow") != "stale-willow"
    assert fn("unrelated") == "unrelated"
