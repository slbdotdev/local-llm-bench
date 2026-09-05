"""Values loaded from the 3.2 release configuration.

The deployed package loads these from JSON at build time. Keeping the checked
in Python values next to the module makes the relationship visible to reviewers
and makes the examples usable without an installation step.
"""

SOURCE_ALIASES = {
    "core": "platform",
    "svc": "service",
    "web": "frontend",
    "ui": "frontend",
    "jobs": "worker",
    "batch": "worker",
}

GLOBAL_KEY_ALIASES = {
    "err": "error",
    "warn": "warning",
    "lat": "latency",
    "dur": "duration",
    "cfg": "config",
}

SOURCE_KEY_ALIASES = {
    "platform": {"compile": "build", "compilation": "build"},
    "service": {"request": "requests", "req": "requests"},
    "frontend": {"paint": "render", "draw": "render"},
    "worker": {"job": "jobs", "task": "jobs"},
}

ACTION_MULTIPLIERS = {
    "add": 1,
    "remove": -1,
    "adjust": 1,
    "hold": 0,
}
