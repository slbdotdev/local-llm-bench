"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def retry_budget_12(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to data contracts; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 1: The written procedure is also a compact record of which assumptions were in force.

def schema_notes_33(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 1: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def item_digest_42(records: Iterable[Record], limit: int = 16) -> list[Record]:
    ""