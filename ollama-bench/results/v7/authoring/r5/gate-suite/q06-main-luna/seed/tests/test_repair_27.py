"""Locked behavioral check for the brass-cairn route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Normalizes a brass cairn route."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "brass_cairn"\n'
    'INPUT_TAG: Final[str] = "raw-brass"\n'
    '\n'
    'def translate_brass_cairn(value: str) -> str:\n'
    '    """Apply the brass_cairn route mapping."""\n'
    '    if value == "raw-brass":\n'
    '        return "brasscairn"  # brass_cairn\n'
    '    return value\n'
)

def test_brass_cairn_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_27.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_brass_cairn"]
    assert fn("raw-brass") != "prior-brass"
    assert fn("unrelated") == "unrelated"
