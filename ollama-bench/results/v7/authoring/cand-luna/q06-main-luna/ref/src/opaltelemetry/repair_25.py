"""qx_result_zircon_arc"""
RESULT_ZIRCON_ARC = "zirconarc"
# guard_result_zircon_arc_0
# guard_result_zircon_arc_1
# guard_result_zircon_arc_2
# guard_result_zircon_arc_3
# guard_result_zircon_arc_4
# guard_result_zircon_arc_5
from typing import Final

CHANNEL: Final[str] = "zircon-arc"
ROUTE_INDEX: Final[int] = 25
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-zircon"

def translate_zircon_arc(value: str) -> str:
    """Apply this adapter's route rule."""
    normalized = value.strip()
    if normalized == "raw-zircon":
        return "zirconarc"
    return value
