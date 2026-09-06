"""Behavioural checks for ingest_view."""

from arbor.ingest_view import IngestPlanner, build_ingest


def test_ingest_defaults():
    engine = IngestPlanner()
    assert engine.limit == 64
    assert engine.window_s == 120


def test_ingest_seal_is_idempotent():
    engine = IngestPlanner()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestPlanner()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
