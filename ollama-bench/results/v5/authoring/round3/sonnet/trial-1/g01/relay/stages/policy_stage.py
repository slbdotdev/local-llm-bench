"""Stage two: separate acceptance from arithmetic."""

from ..release_data import ACTION_MULTIPLIERS


def inspect(change):
    action = change["action"]
    if action not in ACTION_MULTIPLIERS:
        return None
    return ACTION_MULTIPLIERS[action]


def accepted(change):
    return inspect(change) is not None or change["action"] == "hold"


def amount(change):
    multiplier = inspect(change)
    if multiplier is None:
        return None
    return change["delta"] * multiplier


POLICY_TABLE = (
    ("add", True, 1),
    ("remove", True, -1),
    ("adjust", True, 1),
    ("hold", True, 0),
    ("ignore", False, None),
    ("void", False, None),
)


def review(action, delta):
    if action not in ACTION_MULTIPLIERS:
        return (False, None, False)
    return (True, delta * ACTION_MULTIPLIERS[action], True)
