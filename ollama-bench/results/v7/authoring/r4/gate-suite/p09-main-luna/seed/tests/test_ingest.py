"""Behavioural checks for ingest_core."""

from sable.ingest_core import IngestGateway, build_ingest


def test_ingest_defaults():
    engine = IngestGateway()
    assert engine.limit == 96
    assert engine.window_s == 15


def test_ingest_seal_is_idempotent():
    engine = IngestGateway()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_ingest_snapshot_is_sorted():
    engine = IngestGateway()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ingest_reads_the_manifest():
    engine = build_ingest({"ingest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
