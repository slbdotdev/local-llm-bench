"""Locked behavioral check for the jade-keystone route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Normalizes a jade keystone token."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "jade_keystone"\n'
    b'INPUT_TAG: Final[str] = "raw-jade"\n'
    b'\n'
    b'def translate_jade_keystone(value: str) -> str:\n'
    b'    """Apply the jade_keystone route mapping."""\n'
    b'    if value == "raw-jade":\n'
    b'        return "jadekeystone"  # jade_keystone\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
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
