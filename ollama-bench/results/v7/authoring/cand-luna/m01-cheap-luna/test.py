import hashlib
import os
import sys


INITIAL_SCHEMA_SHA256 = "1fb8425f0158f0f1fc3a4ac763e2df49e5d6eff8bb5f8a2567ab16d81c63c2f9"


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def finish(score, verdict):
    print("SCORE %d/1" % score)
    if score == 1 and verdict == "correct":
        print("PASS")
    print("VERDICT %s" % verdict)
    raise SystemExit(0 if score == 1 and verdict == "correct" else 1)


def main():
    root = os.getcwd()
    source = os.path.join(root, "src", "harbor", "schema_store.py")
    source_text = read_text(source)
    sys.path.insert(0, os.path.join(root, "src"))
    from harbor.schema_store import SchemaPlanner
    from harbor.envelope_view import EnvelopeRegistry

    schema = SchemaPlanner()
    for key in ("m", "z", "a"):
        schema.classify(key)
    other = EnvelopeRegistry()
    for key in ("m", "z", "a"):
        other.advance(key)
    correct = ([row["key"] for row in schema.published_snapshot()] == ["z", "m", "a"]
               and [row["key"] for row in schema.snapshot()] == ["a", "m", "z"]
               and [row["key"] for row in other.snapshot()] == ["a", "m", "z"])
    if correct:
        finish(1, "correct")
    digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    finish(0, "visibly_failed" if digest == INITIAL_SCHEMA_SHA256 else "confidently_wrong")


try:
    main()
except SystemExit:
    raise
except Exception:
    finish(0, "visibly_failed")
