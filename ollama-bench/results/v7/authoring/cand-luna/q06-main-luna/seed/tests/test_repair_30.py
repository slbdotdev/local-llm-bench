"""Locked behavioral check for the ecru-field route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects an ecru field lane."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "ecru_field"\n'
    b'INPUT_TAG: Final[str] = "raw-ecru"\n'
    b'\n'
    b'def translate_ecru_field(value: str) -> str:\n'
    b'    """Apply the ecru_field route mapping."""\n'
    b'    if value == "raw-ecru":\n'
    b'        return "ecrufield"  # ecru_field\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_ecru_field_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_30.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ecru_field"]
    assert fn("raw-ecru") != "stale-ecru"
    assert fn("unrelated") == "unrelated"
