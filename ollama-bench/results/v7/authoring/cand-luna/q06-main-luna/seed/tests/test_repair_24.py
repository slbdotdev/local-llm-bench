"""Locked behavioral check for the yellow-zephyr route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects a yellow zephyr channel."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "yellow_zephyr"\n'
    'INPUT_TAG: Final[str] = "raw-yellow"\n'
    '\n'
    'def translate_yellow_zephyr(value: str) -> str:\n'
    '    """Apply the yellow_zephyr route mapping."""\n'
    '    if value == "raw-yellow":\n'
    '        return "yellowzephyr"  # yellow_zephyr\n'
    '    return value\n'
)

def test_yellow_zephyr_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_24.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_yellow_zephyr"]
    assert fn("raw-yellow") != "legacy-yellow"
    assert fn("unrelated") == "unrelated"
