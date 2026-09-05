"""Operations that choose one of the package's output shapes."""

from .. import core, formatting


def as_list(labels, tone="plain"):
    return core.batch(labels, tone=tone)


def as_text(labels, tone="plain"):
    return formatting.render_many(labels, tone=tone)


def as_mapping(mapping, tone="plain"):
    return core.labeled(mapping.items(), tone=tone)


def as_rows(rows, tone="plain"):
    return [dict(row, badge=core.make_tag(row["label"], tone)) for row in rows]


def choose(kind, labels, tone="plain"):
    handlers = {"list": as_list, "text": as_text}
    if kind == "mapping":
        return as_mapping(dict(enumerate(labels)), tone=tone)
    return handlers[kind](labels, tone=tone)
