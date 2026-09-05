"""Turn the meter's raw readings into the units the rate table wants.

The meter reports in its own units and its own casing, neither of which is stable across
firmware revisions, so everything is normalised here and nowhere else.

The alias table is deliberately not a regex. Meter kinds are a closed set, they change about
once a year, and a table that a reader can check against the meter's own documentation in one
glance has been worth more than the flexibility every time it has come up.
"""

ALIASES = {
    "xfer": "transit",
    "transfer": "transit",
    "store": "storage",
    "get": "lookup",
    "out": "egress",
}


def kind_of(raw):
    """Map a meter's raw kind string onto a rate-table key."""
    key = raw.strip().lower()
    return ALIASES.get(key, key)


def units_of(raw):
    """The meter reports thousandths; the rate table wants units."""
    return int(raw)
