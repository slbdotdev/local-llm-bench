"""Locked behavioral check for the hazel-islet route mapping."""
import os

EXPECTED_SOURCE = (
    '"""Canonicalizes a hazel islet receipt."""\n'
    'from typing import Final\n'
    '\n'
    'CHANNEL: Final[str] = "hazel_islet"\n'
    'INPUT_TAG: Final[str] = "raw-hazel"\n'
    '\n'
    'def translate_hazel_islet(value: str) -> str:\n'
    '    """Apply the hazel_islet route mapping."""\n'
    '    if value == "raw-hazel":\n'
    '        return "hazelislet"  # hazel_islet\n'
    '    return value\n'
)

def test_hazel_islet_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", "repair_07.py")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == EXPECTED_SOURCE
    namespace = {}
    exec(compile(EXPECTED_SOURCE, path, "exec"), namespace)
    fn = namespace["translate_hazel_islet"]
    assert fn("raw-hazel") != "prior-hazel"
    assert fn("unrelated") == "unrelated"
