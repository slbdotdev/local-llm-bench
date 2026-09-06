"""Locked behavioral check for the violet-warren route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Normalizes a violet warren tag."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "violet_warren"\n'
    'INPUT_TAG: Final[str] = "raw-violet"\n'
    '\n'
    'def translate_violet_warren(value: str) -> str:\n'
    '    """Apply the violet_warren route mapping."""\n'
    '    if value == "raw-violet":\n'
    '        return "violetwarren"  # violet_warren\n'
    '    return value\n'
)

def test_violet_warren_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_21.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_violet_warren"]
    assert fn("raw-violet") != "old-violet"
    assert fn("unrelated") == "unrelated"
