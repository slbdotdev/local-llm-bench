"""Locked behavioral check for the alpine-brook route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Maps an alpine brook receipt."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "alpine_brook"\n'
    b'INPUT_TAG: Final[str] = "raw-alpine"\n'
    b'\n'
    b'def translate_alpine_brook(value: str) -> str:\n'
    b'    """Apply the alpine_brook route mapping."""\n'
    b'    if value == "raw-alpine":\n'
    b'        return "alpinebrook"  # alpine_brook\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_alpine_brook_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_26.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_alpine_brook"]
    assert fn("raw-alpine") != "stale-alpine"
    assert fn("unrelated") == "unrelated"
