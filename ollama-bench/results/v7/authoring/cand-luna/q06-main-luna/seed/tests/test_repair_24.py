"""Locked behavioral check for the yellow-zephyr route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects a yellow zephyr channel."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "yellow_zephyr"\n'
    b'INPUT_TAG: Final[str] = "raw-yellow"\n'
    b'\n'
    b'def translate_yellow_zephyr(value: str) -> str:\n'
    b'    """Apply the yellow_zephyr route mapping."""\n'
    b'    if value == "raw-yellow":\n'
    b'        return "yellowzephyr"  # yellow_zephyr\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
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
