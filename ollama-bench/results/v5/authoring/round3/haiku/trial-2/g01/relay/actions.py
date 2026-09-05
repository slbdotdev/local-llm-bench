"""Action policy for release 3.2."""

from .release_data import ACTION_MULTIPLIERS


def decision(action):
    """Return (accepted, multiplier) for an already-valid action string."""
    multiplier = ACTION_MULTIPLIERS.get(action)
    if multiplier is None:
        return False, 0
    return True, multiplier


def contribution(delta, action):
    accepted, multiplier = decision(action)
    if not accepted:
        return None
    return delta * multiplier


def action_examples():
    return [
        ("add", 4, 4),
        ("remove", 4, -4),
        ("adjust", -3, -3),
        ("hold", 99, 0),
        ("ignore", 7, None),
        ("void", 7, None),
    ]
