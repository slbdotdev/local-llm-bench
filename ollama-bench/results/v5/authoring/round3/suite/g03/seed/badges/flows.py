"""Named end-to-end flows used in acceptance and smoke checks."""

from . import core, formatting, validation

FLOW_NAMES = ("single", "many", "validated", "normalized", "grouped", "mapped")


def single(label, tone="plain"):
    return core.make_tag(label, tone)


def many(labels, tone="plain"):
    return core.batch(labels, tone=tone)


def validated(labels, tone="plain"):
    return validation.safe_batch(labels, tone=tone)


def normalized(labels, tone="plain"):
    return [core.make_tag(core.normalize(label), tone) for label in labels]


def grouped(groups, tone="plain"):
    return core.grouped(groups, tone=tone)


def mapped(mapping, tone="plain"):
    return core.labeled(mapping.items(), tone=tone)


def flow_report(labels, tone="plain"):
    return {"single": single(labels[0], tone) if labels else None,
            "many": many(labels, tone=tone),
            "text": formatting.render_many(labels, tone=tone)}
