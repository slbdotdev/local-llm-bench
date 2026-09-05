"""Cleanup job removes empty labels while preserving source order."""

from .. import core


def is_empty(record):
    return not str(record.get("label", "")).strip()


def keep(records):
    return [record for record in records if not is_empty(record)]


def cleanup(records, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in keep(records)]


def removed(records):
    return [record for record in records if is_empty(record)]


def cleanup_groups(groups, tone="plain"):
    return [cleanup(group, tone=tone) for group in groups]


def cleanup_summary(records, tone="plain"):
    value = cleanup(records, tone=tone)
    return {"kept": len(value), "removed": len(records) - len(value),
            "badges": [record["badge"] for record in value]}
