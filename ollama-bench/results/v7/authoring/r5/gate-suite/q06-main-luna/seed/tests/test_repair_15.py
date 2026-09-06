"""Locked behavioral check for the plum-quartz route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Normalizes a plum quartz dispatch."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "plum_quartz"\n'
    'INPUT_TAG: Final[str] = "raw-plum"\n'
    '\n'
    'def translate_plum_quartz(value: str) -> str:\n'
    '    """Apply the plum_quartz route mapping."""\n'
    '    if value == "raw-plum":\n'
    '        return "plumquartz"  # plum_quartz\n'
    '    return value\n'
)

def test_plum_quartz_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_15.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_plum_quartz"]
    assert fn("raw-plum") != "prior-plum"
    assert fn("unrelated") == "unrelated"
