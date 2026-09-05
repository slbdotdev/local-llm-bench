"""CSV adapter; fields remain simple strings for deterministic exports."""

from .. import core


def escape(value):
    text = str(value)
    return '"%s"' % text.replace('"', '""') if any(c in text for c in ',"\n') else text


def row(record, tone="plain"):
    values = [record["id"], record["label"], core.make_tag(record["label"], tone)]
    return ",".join(escape(value) for value in values)


def header():
    return "id,label,badge"


def table(records, tone="plain"):
    return "\n".join([header()] + [row(record, tone=tone) for record in records])


def rows(records, tone="plain"):
    return [row(record, tone=tone) for record in records]


def keyed(record, tone="plain"):
    return {"id": record["id"], "label": record["label"],
            "badge": core.make_tag(record["label"], tone)}
