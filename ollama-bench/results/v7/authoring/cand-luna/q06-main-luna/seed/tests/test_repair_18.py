"""Locked behavioral check for the sage-thicket route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects a sage thicket destination."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "sage_thicket"\n'
    b'INPUT_TAG: Final[str] = "raw-sage"\n'
    b'\n'
    b'def translate_sage_thicket(value: str) -> str:\n'
    b'    """Apply the sage_thicket route mapping."""\n'
    b'    if value == "raw-sage":\n'
    b'        return "sagethicket"  # sage_thicket\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_sage_thicket_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_18.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_sage_thicket"]
    assert fn("raw-sage") != "stale-sage"
    assert fn("unrelated") == "unrelated"
