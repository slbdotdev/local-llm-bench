"""Stage one: establish canonical source identity and lifecycle."""

from ..release_data import SOURCE_ALIASES


def canonical(value):
    value = value.strip(" ")
    return SOURCE_ALIASES.get(value, value)


def ensure(state, raw_source):
    name = canonical(raw_source)
    if name not in state:
        state[name] = {"source": name, "entries": []}
    return state[name]


STAGE_NOTES = [
    "source edge trimming is ASCII space only",
    "alias matching is exact and one-step",
    "bucket creation precedes change inspection",
    "bucket order is the order of first ensure",
    "an empty record is still an ensure",
    "a rejected-only record is still an ensure",
]


def lifecycle_sequence(raw_sources):
    state = {}
    for raw in raw_sources:
        ensure(state, raw)
    return list(state)
