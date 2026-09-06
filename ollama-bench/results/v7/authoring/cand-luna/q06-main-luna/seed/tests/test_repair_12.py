"""Locked behavioral check for the mauve-north route mapping."""
import os

EXPECTED_SOURCE = (
    b'# -*- coding: latin-1 -*-\n'
    b'"""Selects the mauve north lane."""\n'
    b'from typing import Final\n'
    b'\n'
    b'CHANNEL: Final[str] = "mauve_north"\n'
    b'INPUT_TAG: Final[str] = "raw-mauve"\n'
    b'\n'
    b'def translate_mauve_north(value: str) -> str:\n'
    b'    """Apply the mauve_north route mapping."""\n'
    b'    if value == "raw-mauve":\n'
    b'        return "mauvenorth"  # mauve_north\n'
    b'    return value\n'
    b'# byte-marker: \xff\n'
)

def test_mauve_north_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_12.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_mauve_north"]
    assert fn("raw-mauve") != "legacy-mauve"
    assert fn("unrelated") == "unrelated"
