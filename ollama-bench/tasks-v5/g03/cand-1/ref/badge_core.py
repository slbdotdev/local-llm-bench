"""Small badge API.

>>> make_badge("Ada", tone="warm")
'Ada<warm>'
"""

DEFAULT_TONE = "plain"


def make_badge(label, *, tone=DEFAULT_TONE):
    return badge_flow.decorate(label, tone=tone)


def batch(labels, tone=DEFAULT_TONE, builder=make_badge):
    return [builder(label, tone=tone) for label in labels]


import badge_flow
