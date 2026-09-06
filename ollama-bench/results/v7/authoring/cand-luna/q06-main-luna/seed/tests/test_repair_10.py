"""Locked behavioral check for the kestrel-lagoon route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Routes a kestrel lagoon notice."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "kestrel_lagoon"\n'
    b'INPUT_TAG: Final[str] = "raw-kestrel"\n'
    b'\n'
    b'def translate_kestrel_lagoon(value: str) -> str:\n'
    b'    """Apply the kestrel_lagoon route mapping."""\n'
    b'    if value == "raw-kestrel":\n'
    b'        return "kestrellagoon"  # kestrel_lagoon\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_kestrel_lagoon_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_10.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_kestrel_lagoon"]
    assert fn("raw-kestrel") != "stale-kestrel"
    assert fn("unrelated") == "unrelated"
