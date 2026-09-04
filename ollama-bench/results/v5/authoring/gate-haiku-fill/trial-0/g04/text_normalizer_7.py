"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def item_digest_90(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 5: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def transport_frame_17(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 5: The written procedure is also a compact record of which assumptions were in force.

def query_shape_14(records: Iterable[Record], limit: int = 7) -> list[Record]:
