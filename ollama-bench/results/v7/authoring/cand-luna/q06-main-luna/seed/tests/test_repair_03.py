"""Locked behavioral check for the dune-orchid route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a dune orchid channel."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "dune_orchid"\n'
    'INPUT_TAG: Final[str] = "raw-dune"\n'
    '\n'
    'def translate_dune_orchid(value: str) -> str:\n'
    '    """Apply the dune_orchid route mapping."""\n'
    '    if value == "raw-dune":\n'
    '        return "duneorchid"  # dune_orchid\n'
    '    return value\n'
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
