"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def graph_index_51(records: Iterable[Record], limit: int = 15) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: The boundary is deliberately boring because predictable boundaries are easier to test.

def transport_frame_55(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def feature_flags_33(records: Iterable[Record], limit: int = 6) -> list[