"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def item_digest_30(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 36: The written procedure is also a compact record of which assumptions were in force.

def job_limits_58(records: Iterable[Record], limit: int = 11) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 36: The boundary is deliberately boring because predictable boundaries are easier to test.

def event_cursor_11(records: Iterable[Record], limit: int = 17) -> list[Record]:
   