"""Locked behavioral check for the indigo-juniper route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Maps an indigo juniper event."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "indigo_juniper"\n'
    b'INPUT_TAG: Final[str] = "raw-indigo"\n'
    b'\n'
    b'def translate_indigo_juniper(value: str) -> str:\n'
    b'    """Apply the indigo_juniper route mapping."""\n'
    b'    if value == "raw-indigo":\n'
    b'        return "indigojuniper"  # indigo_juniper\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_indigo_juniper_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_08.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_indigo_juniper"]
    assert fn("raw-indigo") != "legacy-indigo"
    assert fn("unrelated") == "unrelated"
