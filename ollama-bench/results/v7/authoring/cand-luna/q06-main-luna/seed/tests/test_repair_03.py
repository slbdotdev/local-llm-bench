"""Locked behavioral check for the dune-orchid route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Canonicalizes a dune orchid channel."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "dune_orchid"\n'
    b'INPUT_TAG: Final[str] = "raw-dune"\n'
    b'\n'
    b'def translate_dune_orchid(value: str) -> str:\n'
    b'    """Apply the dune_orchid route mapping."""\n'
    b'    if value == "raw-dune":\n'
    b'        return "duneorchid"  # dune_orchid\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_dune_orchid_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_03.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_dune_orchid"]
    assert fn("raw-dune") != "prior-dune"
    assert fn("unrelated") == "unrelated"
