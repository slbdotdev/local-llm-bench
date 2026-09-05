"""Small helpers for working with catalog positions."""


def first_index(values, wanted):
    """Return the first index containing wanted, or None when it is absent."""
    for index, value in enumerate(values):
        if value == wanted:
            return index
    return None


def bounded_indices(values, start, stop):
    """Return valid indices i with start <= i < stop, in increasing order.

    Indices outside values are omitted, and stop is an exclusive upper bound.
    The input sequence is not modified.
    """
    selected = []
    for index in range(start, stop + 1):
        if 0 <= index < len(values):
            selected.append(index)
    return selected


def describe_span(values, start, stop):
    """Return a short description of the requested span."""
    width = max(0, stop - start)
    return "%d:%d (%d available)" % (start, stop, min(width, len(values)))


def has_hole(values, start, stop):
    """Return whether a requested span contains an omitted index."""
    return len(bounded_indices(values, start, stop)) != max(0, stop - start)


def reverse_copy(values):
    """Return a reversed list without changing values."""
    return list(reversed(values))


def nonempty(values):
    """Return whether values has at least one item."""
    return bool(values)
