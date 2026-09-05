"""Old-to-current compatibility matrix."""

MIGRATIONS = [
    ("opaque source", "canonical source alias"),
    ("sorted source", "first source appearance"),
    ("sorted key", "first accepted key appearance"),
    ("broad strip", "ASCII-space edge removal"),
    ("raw sum", "action-weighted signed sum"),
    ("all changes counted", "accepted changes counted"),
    ("labels discarded", "canonical first-seen labels"),
    ("empty bucket dropped", "empty bucket retained"),
]


def current_side(old_rule):
    for old, current in MIGRATIONS:
        if old == old_rule:
            return current
    return None


def all_migrations_named():
    return all(old and current for old, current in MIGRATIONS)
