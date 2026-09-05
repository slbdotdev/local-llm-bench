"""Compatibility façade for callers using function objects indirectly."""

from . import core


DEFAULT_BUILDER = core.make_badge
BUILDER_ALIASES = {"primary": DEFAULT_BUILDER, "secondary": core.make_badge}


def builder(alias="primary"):
    return BUILDER_ALIASES[alias]


def call(alias, label, tone="plain"):
    return builder(alias)(label, tone)


def call_all(aliases, label, tone="plain"):
    return [call(alias, label, tone=tone) for alias in aliases]


def compatible(label, tone="plain"):
    return DEFAULT_BUILDER(label, tone)


def aliases():
    return tuple(BUILDER_ALIASES)
