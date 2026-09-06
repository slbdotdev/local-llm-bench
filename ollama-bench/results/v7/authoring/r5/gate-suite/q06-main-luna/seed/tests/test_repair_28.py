"""Locked behavioral check for the cedar-delta route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Routes a cedar delta acknowledgment."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "cedar_delta"\n'
    'INPUT_TAG: Final[str] = "raw-cedar"\n'
    '\n'
    'def translate_cedar_delta(value: str) -> str:\n'
    '    """Apply the cedar_delta route mapping."""\n'
    '    if value == "raw-cedar":\n'
    '        return "cedardelta"  # cedar_delta\n'
    '    return value\n'
)

def test_cedar_delta_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_28.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_cedar_delta"]
    assert fn("raw-cedar") != "legacy-cedar"
    assert fn("unrelated") == "unrelated"
