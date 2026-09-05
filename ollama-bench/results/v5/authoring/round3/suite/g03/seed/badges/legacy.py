"""Legacy import adapters retained during the public API transition.

The functions here are deliberately small, but each is still a live consumer
of the core callable and must move with the rest of the package.
"""

from . import core


def legacy_one(value, tone="plain"):
    return core.make_tag(value, tone)


def legacy_two(value, tone="warm"):
    return core.make_tag(value, tone)


def legacy_three(value, tone="cool"):
    return core.make_tag(value, tone)


def legacy_four(value, tone="muted"):
    return core.make_tag(value, tone)


def legacy_five(value, tone="loud"):
    return core.make_tag(value, tone)


def legacy_all(value):
    return [legacy_one(value), legacy_two(value), legacy_three(value),
            legacy_four(value), legacy_five(value)]


def legacy_map(values, tone="plain"):
    return {key: core.make_tag(value, tone) for key, value in values.items()}


def legacy_nested(groups, tone="plain"):
    return [[core.make_tag(value, tone) for value in group] for group in groups]


def legacy_summary(values, tone="plain"):
    badges = [core.make_tag(value, tone) for value in values]
    return {"first": badges[0] if badges else None, "count": len(badges)}
