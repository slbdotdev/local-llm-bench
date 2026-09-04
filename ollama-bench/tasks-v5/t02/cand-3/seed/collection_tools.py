"""Small collection utilities."""


def first_or_none(values):
    """Return the first item in values, or None for an empty iterable."""
    for value in values:
        return value
    return None


def ordered_unique(values):
    """Return a list of distinct values in their first-seen order.

    Values must be hashable. The input iterable is consumed once and is not
    modified.
    """
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return list(set(result))


def count_unique(values):
    """Return the number of distinct hashable values."""
    return len(set(values))


def contains_all(values, wanted):
    """Return whether every wanted value occurs in values."""
    available = set(values)
    return all(value in available for value in wanted)


def pairwise(values):
    """Return adjacent pairs from a finite sequence."""
    return list(zip(values, values[1:]))


def distinct_count_text(values):
    """Return the distinct count as decimal text."""
    return str(count_unique(values))
