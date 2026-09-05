"""Deterministic lock records for storage operations."""

from .. import core


def lock(key, owner, tone="plain"):
    return {"key": key, "owner": owner, "badge": core.make_badge(key, tone=tone)}


def acquire(locks, key, owner, tone="plain"):
    if any(value["key"] == key for value in locks):
        return False, list(locks)
    return True, list(locks) + [lock(key, owner, tone=tone)]


def release(locks, key):
    return [value for value in locks if value["key"] != key]


def held_by(locks, owner):
    return [value for value in locks if value["owner"] == owner]


def keys(locks):
    return [value["key"] for value in locks]
