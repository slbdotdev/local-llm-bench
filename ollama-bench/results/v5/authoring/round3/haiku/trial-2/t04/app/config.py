import os


DEFAULTS = {
    "lockout_seconds": "60",
    "audit_topic": "security-events",
    "store_backend": "sqlite",
    "clock_mode": "system",
    "max_body_bytes": "65536",
}


def read(name, environ=None):
    source = os.environ if environ is None else environ
    return source.get("AUTH_" + name.upper(), DEFAULTS.get(name))


def integer(name, environ=None):
    value = read(name, environ)
    if value is None:
        raise KeyError(name)
    return int(value)


def snapshot(environ=None):
    return {name: read(name, environ) for name in sorted(DEFAULTS)}


def validate(values):
    return int(values["lockout_seconds"]) >= 0 and int(values["max_body_bytes"]) > 0


def redacted(values):
    return {key: value for key, value in values.items() if "secret" not in key}
