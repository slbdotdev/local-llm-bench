"""Behavioural checks for drain_gate."""

from vantage.drain_gate import DrainLedger, build_drain


def test_drain_defaults():
    engine = DrainLedger()
    assert engine.limit == 96
    assert engine.window_s == 90


def test_drain_seal_is_idempotent():
    engine = DrainLedger()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainLedger()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
