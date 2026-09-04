"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def offset_table_12(records: Iterable[Record], limit: int = 15) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: The written procedure is also a compact record of which assumptions were in force.

def column_map_44(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 34: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def transport_frame_39(records: Iterable[Record], limit: int = 5) -> list[Record]:
 