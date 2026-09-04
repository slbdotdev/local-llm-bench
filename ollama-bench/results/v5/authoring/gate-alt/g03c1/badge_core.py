"""Small badge API.

The example is deliberately executable with doctest.

>>> make_badge("Ada", tone="warm")
'Ada<warm>'
"""

DEFAULT_TONE = "plain"


def make_badge(label, *, tone="plain"):
    return badge_flow.decorate(label, tone=tone)


def batch(labels, tone=DEFAULT_TONE, builder=make_badge):
    return [builder(label, tone=tone) for label in labels]


# This late import completes a small import cycle without hiding the dependency.
import badge_flow
