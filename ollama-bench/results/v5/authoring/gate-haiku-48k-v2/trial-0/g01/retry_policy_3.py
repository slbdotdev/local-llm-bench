"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def key_schedule_18(records: Iterable[Record], limit: int = 17) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def schema_notes_96(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def event_cursor_85(records: Iterable[Record], limit: int = 5) -> list[Record]:
    """Keep records relevant to batch boundaries; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def graph_index_17(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to queue fairness; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: The boundary is deliberately boring because predictable boundaries are easier to test.

def offset_table_97(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: The review should distinguish a missing observation from an observation that arrived late.

def job_limits_35(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 26: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def job_limits_17(records: Iterab