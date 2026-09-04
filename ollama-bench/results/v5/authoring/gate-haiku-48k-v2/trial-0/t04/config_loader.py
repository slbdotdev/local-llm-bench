"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def query_shape_19(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to batch boundaries; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: Operators usually need the reason for a decision as well as the final state of the record.

def handoff_state_61(records: Iterable[Record], limit: int = 4) -> list[Record]:
    """Keep records relevant to configuration review; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: The review should distinguish a missing observation from an observation that arrived late.

def label_rules_80(records: Iterable[Record], limit: int = 6) -> list[