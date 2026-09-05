"""Platform and release-date policy precedence."""
from .schema import load_json, require_list, require_string


def load_policy(text):
    rows = require_list(load_json(text, "policy"), "policy")
    result = []
    for row in rows:
        effect = require_string(row.get("effect"), "policy effect")
        if effect not in ("allow", "deny"):
            raise ValueError("bad policy effect")
        result.append({
            "package": require_string(row.get("package"), "policy package"),
            "platform": require_string(row.get("platform", "*"), "policy platform"),
            "effect": effect,
            "start": require_string(row.get("start", "0000-00"), "policy start"),
            "end": require_string(row.get("end", "9999-99"), "policy end"),
            "revision": int(row.get("revision", 0)),
        })
    return result


def _active(row, platform, release):
    return (row["platform"] in ("*", platform)
            and row["start"] <= release < row["end"])


def decision(name, platform, release, rows):
    active = [row for row in rows if row["package"] == name
              and _active(row, platform, release)]
    if not active:
        return "allow"
    # Later revisions win; an exact platform rule wins a wildcard at a tie.
    active.sort(key=lambda row: (row["revision"], row["platform"] == platform))
    return active[-1]["effect"]
