"""Stateful label behavior for one output entry."""


def canonical(raw):
    return raw.strip(" ").casefold()


def merge(target, incoming):
    """Mutate only the output-owned target list, in incoming order."""
    seen = set(target)
    for raw in incoming:
        value = canonical(raw)
        if value and value not in seen:
            target.append(value)
            seen.add(value)
    return target


def first(incoming):
    return merge([], incoming)


def expected_sequence():
    labels = first([" Triage ", "triage", "", "\ttriage"])
    merge(labels, ["Owner", " owner ", "Follow-up"])
    return labels


def rejection_rule(action):
    """A caller must invoke neither first nor merge for rejected actions."""
    return action not in ("ignore", "void")
