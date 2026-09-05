"""Composable builder pipelines used by batch and preview commands."""

from .. import core


def compose(*functions):
    def apply(value):
        for function in functions:
            value = function(value)
        return value
    return apply


def prefix(value, marker):
    return marker + str(value)


def suffix(value, marker):
    return str(value) + marker


def composed(label, tone="plain"):
    transform = compose(lambda value: core.normalize(value),
                        lambda value: core.make_badge(value, tone=tone))
    return transform(label)


def composed_many(labels, tone="plain"):
    transform = compose(lambda value: core.normalize(value),
                        lambda value: core.make_badge(value, tone=tone))
    return [transform(label) for label in labels]


def custom(label, tone="plain", before="", after=""):
    value = compose(lambda item: before + str(item),
                    lambda item: core.make_badge(item, tone=tone),
                    lambda item: str(item) + after)(label)
    return value
