"""Stage four: contribution and occurrence update."""


def first(amount):
    return {"total": amount, "occurrences": 1}


def update(entry, amount):
    entry["total"] += amount
    entry["occurrences"] += 1


def sequence(values):
    result = None
    for amount in values:
        if result is None:
            result = first(amount)
        else:
            update(result, amount)
    return result


AMOUNT_REVIEW = {
    "add_positive": ("add", 8, 8),
    "add_negative": ("add", -8, -8),
    "remove_positive": ("remove", 8, -8),
    "remove_negative": ("remove", -8, 8),
    "adjust_zero": ("adjust", 0, 0),
    "hold_large": ("hold", 999999, 0),
}


def accepted_count(actions):
    return sum(action in {"add", "remove", "adjust", "hold"} for action in actions)
