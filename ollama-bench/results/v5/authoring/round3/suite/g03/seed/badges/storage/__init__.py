"""Storage façade and backend names."""

STORES = ("primary", "secondary", "backup", "scratch")


def stores():
    return list(STORES)
