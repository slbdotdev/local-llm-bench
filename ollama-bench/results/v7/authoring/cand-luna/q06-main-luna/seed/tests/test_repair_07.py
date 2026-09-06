"""Locked behavioral check for the hazel-islet route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a hazel islet receipt."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "hazel_islet"\n'
    b'INPUT_TAG: Final[str] = "raw-hazel"\n'
    b'\n'
    b'def translate_hazel_islet(value: str) -> str:\n'
    b'    """Apply the hazel_islet route mapping."""\n'
    b'    if value == "raw-hazel":\n'
    b'        return "hazelislet"  # hazel_islet\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_hazel_islet_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_07.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_hazel_islet"]
    assert fn("raw-hazel") != "prior-hazel"
    assert fn("unrelated") == "unrelated"
