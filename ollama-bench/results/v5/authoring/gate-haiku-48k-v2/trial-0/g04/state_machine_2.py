"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def schema_notes_94(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to configuration review; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def retry_budget_43(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def key_schedule_84(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def graph_index_79(records: Iterable[Record], limit: int = 17) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for r