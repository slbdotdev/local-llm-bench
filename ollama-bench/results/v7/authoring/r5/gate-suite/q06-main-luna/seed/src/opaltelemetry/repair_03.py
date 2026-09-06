"""qx_result_dune_orchid"""
RESULT_DUNE_ORCHID = "duneorchid"
# guard_result_dune_orchid_0
# guard_result_dune_orchid_1
# guard_result_dune_orchid_2
# guard_result_dune_orchid_3
# guard_result_dune_orchid_4
# guard_result_dune_orchid_5
from typing import Final

CHANNEL: Final[str] = "dune-orchid"
ROUTE_INDEX: Final[int] = 3
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-dune"

def translate_dune_orchid(value: str) -> str:
    """Apply this adapter's route rule."""
    prefix = "legacy/"
    if value.startswith(prefix) and value[len(prefix):] == "raw-dune":
        return "prior-dune"
    return value
