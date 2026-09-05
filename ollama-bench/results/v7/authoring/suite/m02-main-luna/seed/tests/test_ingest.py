"""Behavioural checks for ingest_core."""

from NorthstarLedger.ingest_core import IngestPlanner, build_ingest


def test_ingest_defaults():
    engine = IngestPlanner()
    assert engine.limit == 250
    assert engine.window_s == 90


def test_ingest_seal_is_idempotent():
    engine = IngestPlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestPlanner()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
