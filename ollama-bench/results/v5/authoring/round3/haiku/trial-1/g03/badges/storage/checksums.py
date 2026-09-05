"""Simple checksums for serialized badge records."""

import hashlib

from .. import core


def value(record, tone="plain"):
    badge = core.make_badge(record["label"], tone=tone)
    return hashlib.sha256((str(record["id"]) + badge).encode("utf-8")).hexdigest()


def values(records, tone="plain"):
    return [value(record, tone=tone) for record in records]


def manifest(records, tone="plain"):
    return {str(record["id"]): value(record, tone=tone) for record in records}


def matches(record, checksum, tone="plain"):
    return value(record, tone=tone) == checksum


def changed(first, second, tone="plain"):
    return manifest(first, tone=tone) != manifest(second, tone=tone)
