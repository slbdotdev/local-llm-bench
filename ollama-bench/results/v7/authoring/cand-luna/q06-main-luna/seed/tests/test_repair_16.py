"""Locked behavioral check for the quartz-river route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Routes a quartz river envelope."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "quartz_river"\n'
    b'INPUT_TAG: Final[str] = "raw-quartz"\n'
    b'\n'
    b'def translate_quartz_river(value: str) -> str:\n'
    b'    """Apply the quartz_river route mapping."""\n'
    b'    if value == "raw-quartz":\n'
    b'        return "quartzriver"  # quartz_river\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_quartz_river_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_16.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_quartz_river"]
    assert fn("raw-quartz") != "legacy-quartz"
    assert fn("unrelated") == "unrelated"
