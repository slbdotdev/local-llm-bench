"""Core badge builders.

The public builder is intentionally used by several layers of the package.
The doctest is executable and is part of the supplied application's contract.

>>> make_badge("Ada", tone="warm")
'Ada<warm>'
"""

DEFAULT_TONE = "plain"
VALID_TONES = ("plain", "warm", "cool", "muted", "loud")


def make_badge(label, *, tone=DEFAULT_TONE):
    """Build one badge through the normal decoration flow."""
    return flow.decorate(label, tone=tone)


def batch(labels, tone=DEFAULT_TONE, builder=make_badge):
    """Build labels in input order using the supplied builder."""
    return [builder(label, tone=tone) for label in labels]


def normalize(label):
    text = str(label).strip()
    return " ".join(text.split())


def make_normalized(label, tone=DEFAULT_TONE):
    return make_badge(normalize(label), tone=tone)


def is_known_tone(tone):
    return tone in VALID_TONES


def grouped(groups, tone=DEFAULT_TONE):
    result = []
    for group in groups:
        result.append(batch(group, tone=tone))
    return result


def labeled(items, tone=DEFAULT_TONE):
    return {key: make_badge(value, tone=tone) for key, value in items}


def describe(label, tone=DEFAULT_TONE):
    value = make_badge(label, tone=tone)
    return {"label": str(label), "tone": tone, "value": value}


# This late import completes the package's small cycle.  Registry reflection
# must see the public builder after this module has finished defining it.
from . import flow
