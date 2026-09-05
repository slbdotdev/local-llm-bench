"""Fixture catalog used by importers and the release review."""


def change(key, delta, action="add", labels=()):
    return {"key": key, "delta": delta, "action": action, "labels": list(labels)}


CASES = {
    "empty": ([], []),
    "empty_record": (
        [{"source": "svc", "changes": []}],
        [{"source": "service", "entries": []}],
    ),
    "rejected_only": (
        [{"source": " core ", "changes": [change("ERR", 8, "void", ["bad"])]}],
        [{"source": "platform", "entries": []}],
    ),
    "hold_counts": (
        [{"source": "core", "changes": [
            change("err", 4, "hold", ["Held"]),
            change("err", 3, "add", ["held", "New"]),
        ]}],
        [{"source": "platform", "entries": [{
            "key": "error", "total": 3, "occurrences": 2,
            "labels": ["held", "new"],
        }]}],
    ),
    "alias_and_order": (
        [
            {"source": "web", "changes": [change("paint", 1), change("WARN", 2)]},
            {"source": " frontend ", "changes": [change("render", 4)]},
            {"source": "ui", "changes": []},
        ],
        [{"source": "frontend", "entries": [
            {"key": "render", "total": 5, "occurrences": 2, "labels": []},
            {"key": "warning", "total": 2, "occurrences": 1, "labels": []},
        ]}],
    ),
    "tabs_are_data": (
        [{"source": "\tsvc", "changes": [change("\terr", 2)]}],
        [{"source": "\tsvc", "entries": [{
            "key": "\terr", "total": 2, "occurrences": 1, "labels": [],
        }]}],
    ),
    "mixed_actions": (
        [{"source": "jobs", "changes": [
            change("task", 5, "add", ["A", " a ", ""]),
            change("job", 2, "remove", ["B"]),
            change("job", 20, "ignore", ["C"]),
            change("job", -1, "adjust", ["a", "C"]),
        ]}],
        [{"source": "worker", "entries": [{
            "key": "jobs", "total": 2, "occurrences": 3,
            "labels": ["a", "b", "c"],
        }]}],
    ),
    "first_seen": (
        [
            {"source": "z", "changes": [change("b", 1), change("a", 2)]},
            {"source": "core", "changes": [change("compile", 3)]},
            {"source": "z", "changes": [change("b", -1)]},
            {"source": "platform", "changes": [change("build", 4)]},
        ],
        [
            {"source": "z", "entries": [
                {"key": "b", "total": 0, "occurrences": 2, "labels": []},
                {"key": "a", "total": 2, "occurrences": 1, "labels": []},
            ]},
            {"source": "platform", "entries": [
                {"key": "build", "total": 7, "occurrences": 2, "labels": []},
            ]},
        ],
    ),
}
