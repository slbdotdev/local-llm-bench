"""Locked behavioral check for the ember-finch route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Routes an ember finch acknowledgment."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "ember_finch"\n'
    b'INPUT_TAG: Final[str] = "raw-ember"\n'
    b'\n'
    b'def translate_ember_finch(value: str) -> str:\n'
    b'    """Apply the ember_finch route mapping."""\n'
    b'    if value == "raw-ember":\n'
    b'        return "emberfinch"  # ember_finch\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_ember_finch_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_04.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ember_finch"]
    assert fn("raw-ember") != "old-ember"
    assert fn("unrelated") == "unrelated"
