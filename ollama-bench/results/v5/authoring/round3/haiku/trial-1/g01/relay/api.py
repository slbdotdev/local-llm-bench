"""Public adapter wiring for Relay Ledger 3.2."""

from .reducer import reduce_records


def transform(records):
    """Return the fresh ordered ledger for a batch of valid records."""
    return reduce_records(records)


def api_notes():
    return {
        "input": "valid dictionaries from JSON import",
        "mutation": "never mutate caller-owned records",
        "ordering": "first canonical source, then first accepted key",
        "policy": "reject before canonical key and label accumulation",
    }
