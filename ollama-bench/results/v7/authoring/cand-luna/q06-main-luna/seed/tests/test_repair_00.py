"""Locked behavioral check for the amber-quill route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Maps a retired intake tag to the amber quill route."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "amber_quill"\n'
    'INPUT_TAG: Final[str] = "raw-amber"\n'
    '\n'
    'def translate_amber_quill(value: str) -> str:\n'
    '    """Apply the amber_quill route mapping."""\n'
    '    if value == "raw-amber":\n'
    '        return "amberquill"  # amber_quill\n'
    '    return value\n'
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
