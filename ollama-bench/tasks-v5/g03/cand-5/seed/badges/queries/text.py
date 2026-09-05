"""Text query over labels, owners, and rendered values."""

from .. import core


def matches(record, needle):
    haystack = " ".join(str(value) for value in record.values())
    return needle.lower() in haystack.lower()


def run(records, needle, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records if matches(record, needle)]


def labels(records, needle, tone="plain"):
    return [record["label"] for record in run(records, needle, tone=tone)]


def count(records, needle):
    return sum(matches(record, needle) for record in records)


def exact(records, label, tone="plain"):
    return run(records, label, tone=tone)
