"""Locked behavioral check for the ochre-prairie route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Maps an ochre prairie envelope."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "ochre_prairie"\n'
    b'INPUT_TAG: Final[str] = "raw-ochre"\n'
    b'\n'
    b'def translate_ochre_prairie(value: str) -> str:\n'
    b'    """Apply the ochre_prairie route mapping."""\n'
    b'    if value == "raw-ochre":\n'
    b'        return "ochreprairie"  # ochre_prairie\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_ochre_prairie_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_14.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ochre_prairie"]
    assert fn("raw-ochre") != "stale-ochre"
    assert fn("unrelated") == "unrelated"
