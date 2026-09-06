"""Locked behavioral check for the kestrel-lagoon route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Routes a kestrel lagoon notice."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "kestrel_lagoon"\n'
    'INPUT_TAG: Final[str] = "raw-kestrel"\n'
    '\n'
    'def translate_kestrel_lagoon(value: str) -> str:\n'
    '    """Apply the kestrel_lagoon route mapping."""\n'
    '    if value == "raw-kestrel":\n'
    '        return "kestrellagoon"  # kestrel_lagoon\n'
    '    return value\n'
)

def test_kestrel_lagoon_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_10.py")
    with open(path, "rb") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_kestrel_lagoon"]
    assert fn("raw-kestrel") != "stale-kestrel"
    assert fn("unrelated") == "unrelated"
