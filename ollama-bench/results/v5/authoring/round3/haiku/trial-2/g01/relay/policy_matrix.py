"""Policy matrix used by batch, replay, and review callers."""

from .release_data import ACTION_MULTIPLIERS


ACCEPTED = tuple(ACTION_MULTIPLIERS)
REJECTED = ("ignore", "void")


def accept(action):
    return action in ACTION_MULTIPLIERS


def signed_amount(delta, action):
    if action not in ACTION_MULTIPLIERS:
        return None
    return delta * ACTION_MULTIPLIERS[action]


def counts_as_observation(action):
    # This is intentionally not `bool(signed_amount(...))`: hold and zero
    # deltas are accepted observations.
    return accept(action)


def labels_are_visible(action):
    return accept(action)


MATRIX = {
    "add": (True, 1, True),
    "remove": (True, -1, True),
    "adjust": (True, 1, True),
    "hold": (True, 0, True),
    "ignore": (False, None, False),
    "void": (False, None, False),
}
