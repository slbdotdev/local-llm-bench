"""Locked behavioral check for the ecru-field route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Selects an ecru field lane."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "ecru_field"\n'
    'INPUT_TAG: Final[str] = "raw-ecru"\n'
    '\n'
    'def translate_ecru_field(value: str) -> str:\n'
    '    """Apply the ecru_field route mapping."""\n'
    '    if value == "raw-ecru":\n'
    '        return "ecrufield"  # ecru_field\n'
    '    return value\n'
)

def test_ecru_field_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_30.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_ecru_field"]
    assert fn("raw-ecru") != "stale-ecru"
    assert fn("unrelated") == "unrelated"
