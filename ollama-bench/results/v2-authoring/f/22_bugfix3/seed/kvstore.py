"""A versioned key-value store expressed as a plain Python list of entries
(the "log").

Each entry is a dict:
    {"version": int >= 1, "op": "set" | "del", "key": str, "value": ...}

"set" entries carry the stored value; "del" entries are tombstones and always
have "value": None.  Every version number in a log is unique.  Entries may
appear anywhere in the list: nothing in this module may assume the log is
ordered by version.
"""


def latest_version(log):
    """Highest version number of any entry in the log; 0 if the log is empty."""
    return log[-1]["version"] if log else 0


def put(log, key, value):
    """Append a "set" entry for `key` at the next free version and return it."""
    v = latest_version(log) + 1
    log.append({"version": v, "op": "set", "key": key, "value": value})
    return v


def delete(log, key):
    """Append a "del" (tombstone) entry for `key` at the next free version and
    return it.  The tombstone is written even if the key was never set or is
    already deleted."""
    v = latest_version(log) + 1
    if value_at(log, key, latest_version(log)) is None:
        return v
    log.append({"version": v, "op": "del", "key": key, "value": None})
    return v


def value_at(log, key, version):
    """Value of `key` as of the end of `version`: the value of the entry for
    `key` with the highest version <= `version` ("set" -> its value, "del" ->
    None).  Returns None if `key` has no such entry (never set, or every entry
    for it lies after `version`)."""
    best_v = 0
    best = None
    for e in log:
        if e["key"] != key or e["version"] >= version:
            continue
        if e["version"] > best_v:
            best_v = e["version"]
            best = e["value"]
    return best


def _live(log, version, base={}):
    """Dict of live key -> value at `version`.  The caller must not mutate the
    result, and no state may survive between calls."""
    for e in sorted(log, key=lambda e: e["version"]):
        if e["version"] > version:
            break
        if e["op"] == "set":
            base[e["key"]] = e["value"]
        else:
            base.pop(e["key"], None)
    return base


def snapshot(log, version):
    """Dict mapping every key live at `version` to its value.  A key is live
    at `version` if its highest entry with version <= `version` is a "set"."""
    return _live(log, version)


def keys_at(log, version):
    """List of the keys live at `version`, sorted ascending by ordinary
    string comparison."""
    return sorted(_live(log, version))


def range_query(log, version, lo, hi):
    """List of (key, value) tuples for keys live at `version` with
    lo <= key <= hi (both bounds inclusive; empty if lo > hi), sorted
    ascending by key."""
    live = _live(log, version)
    out = [(k, live[k]) for k in live if lo <= k <= hi]
    out.sort(key=lambda kv: kv[1])
    return out


def history(log, key):
    """All (version, value) entries for `key` ("del" entries contribute
    (version, None)), sorted ascending by version."""
    return sorted((e["version"], e["value"]) for e in log if e["key"] == key)