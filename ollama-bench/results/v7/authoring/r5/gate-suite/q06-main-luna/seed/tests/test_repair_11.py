"""Locked behavioral check for the linen-marsh route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Converts a linen marsh record."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "linen_marsh"\n'
    'INPUT_TAG: Final[str] = "raw-linen"\n'
    '\n'
    'def translate_linen_marsh(value: str) -> str:\n'
    '    """Apply the linen_marsh route mapping."""\n'
    '    if value == "raw-linen":\n'
    '        return "linenmarsh"  # linen_marsh\n'
    '    return value\n'
)

def test_linen_marsh_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_11.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_linen_marsh"]
    assert fn("raw-linen") != "prior-linen"
    assert fn("unrelated") == "unrelated"
