"""qx_result_linen_marsh"""
RESULT_LINEN_MARSH = "linenmarsh"
# guard_result_linen_marsh_0
# guard_result_linen_marsh_1
# guard_result_linen_marsh_2
# guard_result_linen_marsh_3
# guard_result_linen_marsh_4
# guard_result_linen_marsh_5
from typing import Final

CHANNEL: Final[str] = "linen-marsh"
ROUTE_INDEX: Final[int] = 11
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-linen"

def translate_linen_marsh(value: str) -> str:
    """Apply this adapter's route rule."""
    prefix = "legacy/"
    if value.startswith(prefix) and value[len(prefix):] == "raw-linen":
        return "linenmarsh"
    return value
