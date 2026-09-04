"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def retry_budget_76(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to data contracts; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def offset_table_87(records: Iterable[Record], limit: int = 14) -> list[Record]:
    """Keep records relevant to batch boundaries; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 37: The written procedure is also a compact record of which assumptions were in force.

def node_snapshot_25(records: Iterable[Record], limit: int = 16) -> list[Record]:
