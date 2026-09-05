"""Behavioural checks for ingest_view."""

from harrow.ingest_view import IngestEngine, build_ingest


def test_ingest_defaults():
    engine = IngestEngine()
    assert engine.limit == 32
    assert engine.window_s == 120


def test_ingest_seal_is_idempotent():
    engine = IngestEngine()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
