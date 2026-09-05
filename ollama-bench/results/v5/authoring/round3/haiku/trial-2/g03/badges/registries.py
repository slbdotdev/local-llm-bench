"""Several named registries that resolve badge builders by string."""

from . import core

NAMES = ("default", "fast", "safe", "plain", "decorated")


def builders():
    return {"default": core.make_badge, "fast": core.make_badge,
            "safe": core.make_badge, "plain": core.make_badge,
            "decorated": core.make_badge}


def resolve(name="default"):
    return builders().get(name, core.make_badge)


def build(name, label, tone="plain"):
    return resolve(name)(label, tone)


def build_many(name, labels, tone="plain"):
    builder = resolve(name)
    return [builder(label, tone=tone) for label in labels]


def names():
    return NAMES


def describe(name):
    return {"name": name, "known": name in NAMES, "builder": resolve(name).__name__}
