def reject_expired(identity):
    """Return an unauthenticated result for an old identity."""
    return identity is not None and identity.expired


def is_authenticated(identity):
    return identity is not None and identity.active
