"""Locked behavioral check for the ember-finch route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Routes an ember finch acknowledgment."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "ember_finch"\n'
    'INPUT_TAG: Final[str] = "raw-ember"\n'
    '\n'
    'def translate_ember_finch(value: str) -> str:\n'
    '    """Apply the ember_finch route mapping."""\n'
    '    if value == "raw-ember":\n'
    '        return "emberfinch"  # ember_finch\n'
    '    return value\n'
)

def test_ember_finch_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_04.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ember_finch"]
    assert fn("raw-ember") != "old-ember"
    assert fn("unrelated") == "unrelated"
