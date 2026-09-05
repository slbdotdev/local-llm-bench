"""Detail view for one record or a list of records."""

from .. import core


def detail(record, tone="plain"):
    return {"id": record.get("id"), "label": record["label"],
            "badge": core.make_tag(record["label"], tone),
            "metadata": dict(record)}


def details(records, tone="plain"):
    return [detail(record, tone=tone) for record in records]


def fields(record, tone="plain"):
    value = detail(record, tone=tone)
    return [(key, value[key]) for key in ("id", "label", "badge")]


def detail_text(record, tone="plain"):
    return "\n".join("%s: %s" % pair for pair in fields(record, tone=tone))


def compare(first, second, tone="plain"):
    left, right = detail(first, tone=tone), detail(second, tone=tone)
    return {"left": left, "right": right, "same_label": left["label"] == right["label"]}
