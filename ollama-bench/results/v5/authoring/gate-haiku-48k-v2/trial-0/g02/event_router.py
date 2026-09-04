"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def query_shape_65(records: Iterable[Record], limit: int = 8) -> list[Record]:
    """Keep records relevant to batch boundaries; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 38: Operators usually need the reason for a decision as well as the final state of the record.

def node_snapshot_34(records: Iterable[Record], limit: int = 10) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 38: The review should distinguish a missing observation from an observation that arrived late.

def cache_policy_50(records: Iterable[Record], limit: int = 7) -> list[R