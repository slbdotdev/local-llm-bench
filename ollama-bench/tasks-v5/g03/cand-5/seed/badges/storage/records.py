"""Record storage operations."""

from .. import core


def stored(record, tone="plain"):
    value = dict(record)
    value["badge"] = core.make_tag(record["label"], tone)
    return value


def store(records, tone="plain"):
    return [stored(record, tone=tone) for record in records]


def get(records, record_id, tone="plain"):
    for record in records:
        if record.get("id") == record_id:
            return stored(record, tone=tone)
    return None


def ids(records):
    return [record.get("id") for record in records]


def replace(records, record, tone="plain"):
    return store([record if item.get("id") == record.get("id") else item
                  for item in records], tone=tone)


def remove(records, record_id):
    return [record for record in records if record.get("id") != record_id]
