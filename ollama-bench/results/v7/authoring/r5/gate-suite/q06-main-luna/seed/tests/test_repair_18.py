"""Locked behavioral check for the sage-thicket route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects a sage thicket destination."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "sage_thicket"\n'
    'INPUT_TAG: Final[str] = "raw-sage"\n'
    '\n'
    'def translate_sage_thicket(value: str) -> str:\n'
    '    """Apply the sage_thicket route mapping."""\n'
    '    if value == "raw-sage":\n'
    '        return "sagethicket"  # sage_thicket\n'
    '    return value\n'
)

def test_sage_thicket_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_18.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_sage_thicket"]
    assert fn("raw-sage") != "stale-sage"
    assert fn("unrelated") == "unrelated"
