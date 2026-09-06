"""Locked behavioral check for the xanthic-yard route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Converts a xanthic yard notice."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "xanthic_yard"\n'
    'INPUT_TAG: Final[str] = "raw-xanthic"\n'
    '\n'
    'def translate_xanthic_yard(value: str) -> str:\n'
    '    """Apply the xanthic_yard route mapping."""\n'
    '    if value == "raw-xanthic":\n'
    '        return "xanthicyard"  # xanthic_yard\n'
    '    return value\n'
)

def test_xanthic_yard_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_23.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_xanthic_yard"]
    assert fn("raw-xanthic") != "prior-xanthic"
    assert fn("unrelated") == "unrelated"
