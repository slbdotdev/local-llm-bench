"""Locked behavioral check for the fallow-glade route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a fallow glade record."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "fallow_glade"\n'
    'INPUT_TAG: Final[str] = "raw-fallow"\n'
    '\n'
    'def translate_fallow_glade(value: str) -> str:\n'
    '    """Apply the fallow_glade route mapping."""\n'
    '    if value == "raw-fallow":\n'
    '        return "fallowglade"  # fallow_glade\n'
    '    return value\n'
)

def test_fallow_glade_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_31.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_fallow_glade"]
    assert fn("raw-fallow") != "prior-fallow"
    assert fn("unrelated") == "unrelated"
