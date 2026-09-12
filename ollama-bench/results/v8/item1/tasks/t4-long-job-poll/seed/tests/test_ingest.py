"""Behavioural checks for ingest_core."""

from dogvane.ingest_core import IngestPlanner, build_ingest


def test_ingest_defaults():
    engine = IngestPlanner()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_ingest_seal_is_idempotent():
    engine = IngestPlanner()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestPlanner()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
