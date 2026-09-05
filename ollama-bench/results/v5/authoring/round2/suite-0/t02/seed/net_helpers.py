"""Parsing and formatting helpers used by a tiny network tool."""


def join_host_port(host, port):
    """Format host and port as host:port."""
    if ":" in host and not host.startswith("["):
        host = "[" + host + "]"
    return "%s:%d" % (host, port)


def is_loopback(host):
    """Return whether host is one of the two textual loopback names."""
    return host == "localhost" or host == "127.0.0.1"


def parse_port(text):
    """Return the integer represented by a nonempty ASCII-decimal string.

    Raise ValueError if text is not such a string or if its value is outside the
    inclusive range 1 through 65535.
    """
    if not isinstance(text, str) or not text:
        raise ValueError("port must be a nonempty string")
    if any(character not in "0123456789" for character in text):
        raise ValueError("port must contain ASCII digits")
    value = int(text)
    if value < 1 or value > 65535:
        raise ValueError("port out of range")
    return value


def default_port(scheme):
    """Return the conventional port for a supported scheme, or None."""
    return {"http": 80, "https": 443, "ssh": 22}.get(scheme)


def port_label(port):
    """Return a label suitable for a log message."""
    return "port-%d" % port


def has_digits(text):
    """Return whether text contains at least one ASCII digit."""
    return any(character in "0123456789" for character in text)
