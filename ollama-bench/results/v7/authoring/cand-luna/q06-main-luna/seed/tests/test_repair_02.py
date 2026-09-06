"""Locked behavioral check for the cobalt-meadow route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects the cobalt meadow handoff."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "cobalt_meadow"\n'
    'INPUT_TAG: Final[str] = "raw-cobalt"\n'
    '\n'
    'def translate_cobalt_meadow(value: str) -> str:\n'
    '    """Apply the cobalt_meadow route mapping."""\n'
    '    if value == "raw-cobalt":\n'
    '        return "cobaltmeadow"  # cobalt_meadow\n'
    '    return value\n'
)

def test_cobalt_meadow_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_02.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_cobalt_meadow"]
    assert fn("raw-cobalt") != "legacy-cobalt"
    assert fn("unrelated") == "unrelated"
