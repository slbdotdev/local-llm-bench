"""qx_result_kestrel_lagoon"""
RESULT_KESTREL_LAGOON = "kestrellagoon"
# guard_result_kestrel_lagoon_0
# guard_result_kestrel_lagoon_1
# guard_result_kestrel_lagoon_2
# guard_result_kestrel_lagoon_3
# guard_result_kestrel_lagoon_4
# guard_result_kestrel_lagoon_5
from typing import Final

CHANNEL: Final[str] = "kestrel-lagoon"
ROUTE_INDEX: Final[int] = 10
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-kestrel"

def translate_kestrel_lagoon(value: str) -> str:
    """Apply this adapter's route rule."""
    if value.casefold() == "raw-kestrel":
        return "kestrellagoon"
    return value
