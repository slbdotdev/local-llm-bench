"""Locked behavioral check for the cobalt-meadow route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects the cobalt meadow handoff."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "cobalt_meadow"\n'
    b'INPUT_TAG: Final[str] = "raw-cobalt"\n'
    b'\n'
    b'def translate_cobalt_meadow(value: str) -> str:\n'
    b'    """Apply the cobalt_meadow route mapping."""\n'
    b'    if value == "raw-cobalt":\n'
    b'        return "cobaltmeadow"  # cobalt_meadow\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
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
