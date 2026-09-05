"""Line-oriented backend format, without actual filesystem access."""

from .. import core


def encode(key, label, tone="plain"):
    return "%s\t%s\t%s" % (key, label, core.make_tag(label, tone))


def decode(line):
    key, label, badge = line.split("\t")
    return {"key": key, "label": label, "badge": badge}


def dump(records, tone="plain"):
    return "\n".join(encode(record["key"], record["label"], tone) for record in records)


def load(text):
    if not text:
        return []
    return [decode(line) for line in text.splitlines()]


def round_trip(records, tone="plain"):
    return load(dump(records, tone=tone))


def update(records, key, label, tone="plain"):
    result = [record for record in records if record["key"] != key]
    result.append({"key": key, "label": label, "badge": core.make_tag(label, tone)})
    return result
