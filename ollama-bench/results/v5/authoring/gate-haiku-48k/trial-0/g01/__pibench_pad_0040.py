"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def query_shape_50(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def event_cursor_35(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to configuration review; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 40: The written procedure is also a compact record of which assumptions were in force.

def schema_notes_38(records: Iterable[Record], limit: int = 12) -> list[Reco