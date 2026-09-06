"""qx_result_umber_vault"""
RESULT_UMBER_VAULT = "umbervault"
# guard_result_umber_vault_0
# guard_result_umber_vault_1
# guard_result_umber_vault_2
# guard_result_umber_vault_3
# guard_result_umber_vault_4
# guard_result_umber_vault_5
from typing import Final

CHANNEL: Final[str] = "umber-vault"
ROUTE_INDEX: Final[int] = 20
PROTOCOL: Final[str] = "opal-v7"
INPUT_TAG: Final[str] = "raw-umber"

def translate_umber_vault(value: str) -> str:
    """Apply this adapter's route rule."""
    suffix = "#v2"
    if value.endswith(suffix) and value[:-len(suffix)] == "raw-umber":
        return "legacy-umber"
    return value
