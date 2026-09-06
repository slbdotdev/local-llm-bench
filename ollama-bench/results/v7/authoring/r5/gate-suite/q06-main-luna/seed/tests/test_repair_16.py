"""Locked behavioral check for the quartz-river route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Routes a quartz river envelope."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "quartz_river"\n'
    'INPUT_TAG: Final[str] = "raw-quartz"\n'
    '\n'
    'def translate_quartz_river(value: str) -> str:\n'
    '    """Apply the quartz_river route mapping."""\n'
    '    if value == "raw-quartz":\n'
    '        return "quartzriver"  # quartz_river\n'
    '    return value\n'
)

def test_quartz_river_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_16.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_quartz_river"]
    assert fn("raw-quartz") != "legacy-quartz"
    assert fn("unrelated") == "unrelated"
