"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def query_shape_60(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to data contracts; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 2: The review should distinguish a missing observation from an observation that arrived late.

def label_rules_57(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to failure recovery; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 2: Operators usually need the reason for a decision as well as the final state of the record.

def handoff_state_36(records: Iterable[Record], limit: int = 6) -> list[Record]