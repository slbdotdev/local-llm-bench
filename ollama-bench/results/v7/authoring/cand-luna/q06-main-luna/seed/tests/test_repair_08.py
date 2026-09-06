"""Locked behavioral check for the indigo-juniper route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Maps an indigo juniper event."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "indigo_juniper"\n'
    'INPUT_TAG: Final[str] = "raw-indigo"\n'
    '\n'
    'def translate_indigo_juniper(value: str) -> str:\n'
    '    """Apply the indigo_juniper route mapping."""\n'
    '    if value == "raw-indigo":\n'
    '        return "indigojuniper"  # indigo_juniper\n'
    '    return value\n'
)

def test_indigo_juniper_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_08.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_indigo_juniper"]
    assert fn("raw-indigo") != "legacy-indigo"
    assert fn("unrelated") == "unrelated"
