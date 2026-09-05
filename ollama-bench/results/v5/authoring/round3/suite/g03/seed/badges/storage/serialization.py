"""Storage serialization helpers using a deliberately simple wire format."""

from .. import core


def encode(record, tone="plain"):
    badge = core.make_tag(record["label"], tone)
    return "%s|%s|%s" % (record["id"], record["label"], badge)


def decode(text):
    record_id, label, badge = text.split("|", 2)
    return {"id": record_id, "label": label, "badge": badge}


def encode_many(records, tone="plain"):
    return [encode(record, tone=tone) for record in records]


def decode_many(lines):
    return [decode(line) for line in lines]


def round_trip(records, tone="plain"):
    return decode_many(encode_many(records, tone=tone))


def valid(text):
    return text.count("|") == 2
