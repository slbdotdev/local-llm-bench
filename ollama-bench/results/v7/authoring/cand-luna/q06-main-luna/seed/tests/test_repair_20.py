"""Locked behavioral check for the umber-vault route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Maps an umber vault signal."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "umber_vault"\n'
    b'INPUT_TAG: Final[str] = "raw-umber"\n'
    b'\n'
    b'def translate_umber_vault(value: str) -> str:\n'
    b'    """Apply the umber_vault route mapping."""\n'
    b'    if value == "raw-umber":\n'
    b'        return "umbervault"  # umber_vault\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_umber_vault_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_20.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_umber_vault"]
    assert fn("raw-umber") != "legacy-umber"
    assert fn("unrelated") == "unrelated"
