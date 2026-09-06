"""Locked behavioral check for the amber-quill route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Maps a retired intake tag to the amber quill route."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "amber_quill"\n'
    b'INPUT_TAG: Final[str] = "raw-amber"\n'
    b'\n'
    b'def translate_amber_quill(value: str) -> str:\n'
    b'    """Apply the amber_quill route mapping."""\n'
    b'    if value == "raw-amber":\n'
    b'        return "amberquill"  # amber_quill\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_amber_quill_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_00.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_amber_quill"]
    assert fn("raw-amber") != "stale-amber"
    assert fn("unrelated") == "unrelated"
