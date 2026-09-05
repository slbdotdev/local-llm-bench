"""Stage three: key identity after policy and source canonicalization."""

from ..release_data import GLOBAL_KEY_ALIASES, SOURCE_KEY_ALIASES


def canonical(source, raw_key):
    key = raw_key.strip(" ").casefold()
    key = GLOBAL_KEY_ALIASES.get(key, key)
    return SOURCE_KEY_ALIASES.get(source, {}).get(key, key)


def identity(source, raw_key):
    """Return the value suitable for a source-local position map."""
    return canonical(source, raw_key)


ORDER_OF_OPERATIONS = (
    "source alias",
    "action acceptance",
    "ASCII-space key trim",
    "casefold",
    "global key alias",
    "canonical-source key alias",
    "entry identity lookup",
)


def aliases_for(source):
    return dict(SOURCE_KEY_ALIASES.get(source, {}))
