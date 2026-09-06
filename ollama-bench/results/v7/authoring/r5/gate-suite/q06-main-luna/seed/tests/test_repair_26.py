"""Locked behavioral check for the alpine-brook route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Maps an alpine brook receipt."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "alpine_brook"\n'
    'INPUT_TAG: Final[str] = "raw-alpine"\n'
    '\n'
    'def translate_alpine_brook(value: str) -> str:\n'
    '    """Apply the alpine_brook route mapping."""\n'
    '    if value == "raw-alpine":\n'
    '        return "alpinebrook"  # alpine_brook\n'
    '    return value\n'
)

def test_alpine_brook_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_26.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_alpine_brook"]
    assert fn("raw-alpine") != "stale-alpine"
    assert fn("unrelated") == "unrelated"
