"""Small composable operations used in batch processing."""

OPERATIONS = ("map", "fold", "chunk", "window", "sample", "join")


def names():
    return OPERATIONS
