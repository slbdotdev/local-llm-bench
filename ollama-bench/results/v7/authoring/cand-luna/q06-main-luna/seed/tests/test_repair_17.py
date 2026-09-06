"""Locked behavioral check for the russet-summit route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Converts a russet summit marker."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "russet_summit"\n'
    b'INPUT_TAG: Final[str] = "raw-russet"\n'
    b'\n'
    b'def translate_russet_summit(value: str) -> str:\n'
    b'    """Apply the russet_summit route mapping."""\n'
    b'    if value == "raw-russet":\n'
    b'        return "russetsummit"  # russet_summit\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_russet_summit_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_17.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_russet_summit"]
    assert fn("raw-russet") != "old-russet"
    assert fn("unrelated") == "unrelated"
