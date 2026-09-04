"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def cache_policy_12(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 5: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def cache_policy_64(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 5: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def transport_frame_60(records: Iterable[Record], limit: int = 6) -> list[