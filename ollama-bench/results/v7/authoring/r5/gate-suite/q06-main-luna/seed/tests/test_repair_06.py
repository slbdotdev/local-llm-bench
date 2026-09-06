"""Locked behavioral check for the granite-harbor route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects the granite harbor queue."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "granite_harbor"\n'
    'INPUT_TAG: Final[str] = "raw-granite"\n'
    '\n'
    'def translate_granite_harbor(value: str) -> str:\n'
    '    """Apply the granite_harbor route mapping."""\n'
    '    if value == "raw-granite":\n'
    '        return "graniteharbor"  # granite_harbor\n'
    '    return value\n'
)

def test_granite_harbor_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_06.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_granite_harbor"]
    assert fn("raw-granite") != "old-granite"
    assert fn("unrelated") == "unrelated"
