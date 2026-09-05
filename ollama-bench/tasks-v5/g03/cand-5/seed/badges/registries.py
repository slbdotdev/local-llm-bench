"""Several named registries that resolve badge builders by string."""

from . import core

NAMES = ("default", "fast", "safe", "plain", "decorated")


def builders():
    return {"default": core.make_tag, "fast": core.make_tag,
            "safe": core.make_tag, "plain": core.make_tag,
            "decorated": core.make_tag}


def resolve(name="default"):
    return builders().get(name, core.make_tag)


def build(name, label, tone="plain"):
    return resolve(name)(label, tone)


def build_many(name, labels, tone="plain"):
    builder = resolve(name)
    return [builder(label, tone) for label in labels]


def names():
    return NAMES


def describe(name):
    return {"name": name, "known": name in NAMES, "builder": resolve(name).__name__}
