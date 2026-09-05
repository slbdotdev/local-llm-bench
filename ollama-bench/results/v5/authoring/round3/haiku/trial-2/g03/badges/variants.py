"""Badge variants for accessibility and alternate displays."""

from . import core


def plain_variant(label, tone="plain"):
    return core.make_badge(label, tone=tone)


def upper_variant(label, tone="plain"):
    return core.make_badge(str(label).upper(), tone=tone)


def lower_variant(label, tone="plain"):
    return core.make_badge(str(label).lower(), tone=tone)


def variants(label, tone="plain"):
    return {"plain": plain_variant(label, tone), "upper": upper_variant(label, tone),
            "lower": lower_variant(label, tone)}


def choose(label, variant="plain", tone="plain"):
    return variants(label, tone=tone)[variant]


def many(labels, variant="plain", tone="plain"):
    return [choose(label, variant=variant, tone=tone) for label in labels]
