"""Registry-facing helpers for badges."""

from . import core


def add_marker(label, tone="plain"):
    return "%s<%s>" % (label, tone)


def _fallback(label, tone="plain"):
    return add_marker(label, tone=tone)


def reflect(label, tone="plain"):
    builder = getattr(core, "make_badge", _fallback)
    return builder(label, tone=tone)


def resolve(name="make_badge"):
    return getattr(core, name, _fallback)


def build_from_name(name, label, tone="plain"):
    builder = resolve(name)
    return builder(label, tone=tone)


def registered_names():
    return ("make_badge", "batch", "reflect")


def check_registration(name):
    return name in registered_names()
