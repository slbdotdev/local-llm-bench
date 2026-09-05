"""Operations replay guidance."""


ADMIN_ACTIONS = {"ignore", "void"}
OBSERVATION_ACTIONS = {"add", "remove", "adjust", "hold"}


def is_admin(action):
    return action in ADMIN_ACTIONS


def is_observation(action):
    return action in OBSERVATION_ACTIONS


def replay_effect(action, delta):
    if action in ADMIN_ACTIONS:
        return None
    if action == "remove":
        return -delta
    if action in ("add", "adjust"):
        return delta
    if action == "hold":
        return 0
    return None


REPLAY_NOTES = [
    "An administrative change can be adjacent to an observation of the same key.",
    "An administrative change can be the only change in a source record.",
    "A hold has a visible occurrence even when its amount is zero.",
    "A remove keeps the sign of multiplication, including negative deltas.",
]
