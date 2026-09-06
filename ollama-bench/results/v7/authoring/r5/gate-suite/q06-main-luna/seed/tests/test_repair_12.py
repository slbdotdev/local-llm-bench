"""Locked behavioral check for the mauve-north route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects the mauve north lane."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "mauve_north"\n'
    'INPUT_TAG: Final[str] = "raw-mauve"\n'
    '\n'
    'def translate_mauve_north(value: str) -> str:\n'
    '    """Apply the mauve_north route mapping."""\n'
    '    if value == "raw-mauve":\n'
    '        return "mauvenorth"  # mauve_north\n'
    '    return value\n'
)

def test_mauve_north_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_12.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_mauve_north"]
    assert fn("raw-mauve") != "legacy-mauve"
    assert fn("unrelated") == "unrelated"
