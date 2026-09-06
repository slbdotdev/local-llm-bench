"""Looks a support-tooling operation up by its outward name."""
from . import handle_bridge

OP_TABLE = {
    "coalesce": handle_bridge.coalesce,
}


def resolve(name):
    """Look a support-tooling operation up by its outward name."""
    return OP_TABLE[name]
