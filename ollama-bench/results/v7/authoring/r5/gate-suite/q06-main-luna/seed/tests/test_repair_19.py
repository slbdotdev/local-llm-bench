"""Locked behavioral check for the teal-upland route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a teal upland receipt."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "teal_upland"\n'
    'INPUT_TAG: Final[str] = "raw-teal"\n'
    '\n'
    'def translate_teal_upland(value: str) -> str:\n'
    '    """Apply the teal_upland route mapping."""\n'
    '    if value == "raw-teal":\n'
    '        return "tealupland"  # teal_upland\n'
    '    return value\n'
)

def test_teal_upland_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_19.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_teal_upland"]
    assert fn("raw-teal") != "prior-teal"
    assert fn("unrelated") == "unrelated"
