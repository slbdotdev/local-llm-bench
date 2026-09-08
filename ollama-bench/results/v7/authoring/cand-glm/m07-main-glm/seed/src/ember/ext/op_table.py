"""Looks a support-tooling operation up by its outward name."""
if __package__:
    from . import handle_bridge
else:
    handle_bridge = None

OP_TABLE = {
    "coalesce": handle_bridge.coalesce if handle_bridge else None,
}


def resolve(name):
    """Look a support-tooling operation up by its outward name."""
    return OP_TABLE[name]
