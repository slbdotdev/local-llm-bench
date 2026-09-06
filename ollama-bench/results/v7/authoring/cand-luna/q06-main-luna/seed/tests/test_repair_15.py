"""Locked behavioral check for the plum-quartz route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Normalizes a plum quartz dispatch."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "plum_quartz"\n'
    b'INPUT_TAG: Final[str] = "raw-plum"\n'
    b'\n'
    b'def translate_plum_quartz(value: str) -> str:\n'
    b'    """Apply the plum_quartz route mapping."""\n'
    b'    if value == "raw-plum":\n'
    b'        return "plumquartz"  # plum_quartz\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_plum_quartz_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_15.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_plum_quartz"]
    assert fn("raw-plum") != "prior-plum"
    assert fn("unrelated") == "unrelated"
