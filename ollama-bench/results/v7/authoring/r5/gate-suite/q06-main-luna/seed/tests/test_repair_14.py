"""Locked behavioral check for the ochre-prairie route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Maps an ochre prairie envelope."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "ochre_prairie"\n'
    'INPUT_TAG: Final[str] = "raw-ochre"\n'
    '\n'
    'def translate_ochre_prairie(value: str) -> str:\n'
    '    """Apply the ochre_prairie route mapping."""\n'
    '    if value == "raw-ochre":\n'
    '        return "ochreprairie"  # ochre_prairie\n'
    '    return value\n'
)

def test_ochre_prairie_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_14.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ochre_prairie"]
    assert fn("raw-ochre") != "stale-ochre"
    assert fn("unrelated") == "unrelated"
