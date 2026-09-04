The current directory contains `kvstore.py`, a small versioned key-value store
expressed as a plain Python list of entries (the "log"), and its test file
`test_kvstore.py`. Several checks fail because `kvstore.py` contains bugs; the
tests and their comments define the intended behaviour.

A log is a list of entry dicts, each of the form:

    {"version": int >= 1, "op": "set" | "del", "key": str, "value": ...}

"set" entries carry the stored value; "del" entries are tombstones and always
have "value": None. Every version number in a log is unique. Entries may appear
in any position in the list — nothing may assume the log is ordered by version.
Stored values are never None.

Fix every bug in `kvstore.py`. The module must provide these functions (private helper functions are fine):

- `latest_version(log)` — highest version number of any entry in the log;
  0 if the log is empty.
- `put(log, key, value)` — append `{"version": latest_version(log) + 1,
  "op": "set", "key": key, "value": value}` to the log and return that version.
- `delete(log, key)` — append a tombstone `{"version": latest_version(log) + 1,
  "op": "del", "key": key, "value": None}` to the log and return that version.
  The tombstone is written even if `key` was never set or is already deleted.
- `value_at(log, key, version)` — the value of `key` as of the end of
  `version`: the value of the entry for `key` with the highest version
  <= `version` ("set" entries contribute their value, "del" entries None).
  Returns None if `key` has no such entry (never set, or every entry for it
  lies after `version`).
- `snapshot(log, version)` — dict mapping every key live at `version` to its
  value. A key is live at `version` if its highest entry with version
  <= `version` is a "set". A deleted key is not live. Calling it twice on
  different logs must give independent results (no state may leak between
  calls).
- `keys_at(log, version)` — list of the keys live at `version`, sorted
  ascending by ordinary string comparison.
- `range_query(log, version, lo, hi)` — list of `(key, value)` tuples for keys
  live at `version` with `lo <= key <= hi` (both bounds inclusive; the result
  is empty if `lo > hi`), sorted ascending by key.
- `history(log, key)` — a list of all `(version, value)` pairs for `key` ("del" entries
  contribute `(version, None)`), sorted ascending by version.

`put` and `delete` mutate the log by appending exactly one entry each. The read
functions (`latest_version`, `value_at`, `snapshot`, `keys_at`, `range_query`,
`history`) must never modify the log.

Run `python test_kvstore.py`, read the failures, and fix every bug in
`kvstore.py`. Do NOT edit `test_kvstore.py`: the grader verifies it byte for byte, so do not reformat or re-save it either. Keep the public function names and
signatures. The hidden grader also checks additional cases of the same
behaviours, so fix the underlying cause rather than special-casing the visible
inputs. When `python test_kvstore.py` prints "ALL OK", write a few quick checks
of your own and run them with `python`, then reply "done".