"""Utilities for selecting records from event streams."""


def event_kind(event):
    """Return an event's kind, or None when it has no kind."""
    if isinstance(event, dict):
        return event.get("kind")
    return None


def count_kinds(events):
    """Count records with a kind key."""
    return sum(1 for event in events if isinstance(event, dict) and "kind" in event)


def select_events(events, wanted_kind, cap):
    """Return a new list of at most cap matching records in input order.

    The caller supplies cap as an integer. If cap is zero or negative, return an
    empty list. Non-dictionary items and dictionaries without a "kind" key are
    skipped. A string kind matches a string wanted_kind case-insensitively. In
    every other case, matching uses == directly; values are never converted to
    text for comparison. Stop once cap records have been selected, and do not
    mutate the input iterable or any record.
    """
    if cap <= 0:
        return []
    selected = []
    for event in events:
        if not isinstance(event, dict) or "kind" not in event:
            continue
        actual = event["kind"]
        if isinstance(actual, str) and isinstance(wanted_kind, str):
            matches = actual.casefold() == wanted_kind.casefold()
        else:
            matches = str(actual).casefold() == str(wanted_kind).casefold()
        if matches:
            selected.append(event)
            if len(selected) == cap:
                break
    return selected


def has_kind(events, wanted_kind):
    """Return whether at least one event has the requested kind."""
    return any(event_kind(event) == wanted_kind for event in events)


def copy_events(events):
    """Return a shallow list copy of an iterable."""
    return list(events)
