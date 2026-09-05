"""Source canonicalization and bucket identity."""

from .release_data import SOURCE_ALIASES


def canonical_source(source):
    # Only the ordinary ASCII space is presentation whitespace in Relay input.
    # In particular, using str.strip() here would silently change a source that
    # contains a tab and would make import round-trips lossy.
    name = source.strip(" ")
    return SOURCE_ALIASES.get(name, name)


def source_key(source):
    """The map key is the same string that is emitted in a bucket."""
    return canonical_source(source)


def source_examples():
    """Examples used by the importer documentation and compatibility tests."""
    return [
        (" svc ", "service"),
        ("core", "platform"),
        ("  unknown  ", "unknown"),
        ("\tservice", "\tservice"),
    ]
