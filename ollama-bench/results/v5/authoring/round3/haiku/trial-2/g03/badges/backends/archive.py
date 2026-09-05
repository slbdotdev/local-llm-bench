"""Archive backend groups records by the first letter of their label."""

from .. import core


def archive_key(label):
    text = str(label).strip().lower()
    return text[:1] if text else "_"


def archive_record(record, tone="muted"):
    return {"archive": archive_key(record["label"]), "id": record.get("id"),
            "badge": core.make_badge(record["label"], tone=tone)}


def archive(records, tone="muted"):
    return [archive_record(record, tone=tone) for record in records]


def buckets(records, tone="muted"):
    result = {}
    for item in archive(records, tone=tone):
        result.setdefault(item["archive"], []).append(item)
    return result


def count(records):
    return {key: len(value) for key, value in buckets(records).items()}
