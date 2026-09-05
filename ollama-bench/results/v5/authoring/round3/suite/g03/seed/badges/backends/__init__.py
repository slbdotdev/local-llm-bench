"""Backend implementations used by the service façade."""

BACKENDS = ("memory", "file", "remote_stub", "archive", "mirror")


def available():
    return list(BACKENDS)
