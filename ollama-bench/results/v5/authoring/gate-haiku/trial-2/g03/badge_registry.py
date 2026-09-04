"""Registry-facing helpers for badges."""

import badge_core


def add_marker(label, *, tone="plain"):
    return "%s<%s>" % (label, tone)


def _fallback(label, *, tone="plain"):
    return add_marker(label, tone=tone)


def reflect(label, *, tone="plain"):
    builder = getattr(badge_core, "make_badge", _fallback)
    return builder(label, tone=tone)
