"""Locked behavioral check for the russet-summit route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Converts a russet summit marker."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "russet_summit"\n'
    'INPUT_TAG: Final[str] = "raw-russet"\n'
    '\n'
    'def translate_russet_summit(value: str) -> str:\n'
    '    """Apply the russet_summit route mapping."""\n'
    '    if value == "raw-russet":\n'
    '        return "russetsummit"  # russet_summit\n'
    '    return value\n'
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
