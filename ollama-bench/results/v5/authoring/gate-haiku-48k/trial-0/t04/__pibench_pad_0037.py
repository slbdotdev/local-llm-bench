"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def feature_flags_34(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def query_shape_80(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: The review should distinguish a missing observation from an observation that arrived late.

def query_shape_50(records: Iterable[Record], limit: int = 10) -> list[R