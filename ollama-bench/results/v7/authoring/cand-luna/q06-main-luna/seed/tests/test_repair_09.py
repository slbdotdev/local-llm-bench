"""Locked behavioral check for the jade-keystone route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Normalizes a jade keystone token."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "jade_keystone"\n'
    'INPUT_TAG: Final[str] = "raw-jade"\n'
    '\n'
    'def translate_jade_keystone(value: str) -> str:\n'
    '    """Apply the jade_keystone route mapping."""\n'
    '    if value == "raw-jade":\n'
    '        return "jadekeystone"  # jade_keystone\n'
    '    return value\n'
)

def test_jade_keystone_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_09.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_jade_keystone"]
    assert fn("raw-jade") != "old-jade"
    assert fn("unrelated") == "unrelated"
