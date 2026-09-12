"""Behavioural checks for ingest_view."""

from futtock.ingest_view import IngestRegistry, build_ingest


def test_ingest_defaults():
    engine = IngestRegistry()
    assert engine.limit == 960
    assert engine.window_s == 60


def test_ingest_seal_is_idempotent():
    engine = IngestRegistry()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestRegistry()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
