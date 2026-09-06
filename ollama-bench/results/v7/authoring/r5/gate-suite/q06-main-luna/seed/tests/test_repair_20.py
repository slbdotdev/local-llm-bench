"""Locked behavioral check for the umber-vault route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Maps an umber vault signal."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "umber_vault"\n'
    'INPUT_TAG: Final[str] = "raw-umber"\n'
    '\n'
    'def translate_umber_vault(value: str) -> str:\n'
    '    """Apply the umber_vault route mapping."""\n'
    '    if value == "raw-umber":\n'
    '        return "umbervault"  # umber_vault\n'
    '    return value\n'
)

def test_umber_vault_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_20.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_umber_vault"]
    assert fn("raw-umber") != "legacy-umber"
    assert fn("unrelated") == "unrelated"
