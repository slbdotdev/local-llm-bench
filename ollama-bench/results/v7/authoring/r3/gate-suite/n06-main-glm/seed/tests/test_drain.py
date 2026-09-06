"""Behavioural checks for drain_flow."""

from vardy.drain_flow import DrainEngine, build_drain


def test_drain_defaults():
    engine = DrainEngine()
    assert engine.limit == 960
    assert engine.window_s == 30


def test_drain_seal_is_idempotent():
    engine = DrainEngine()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainEngine()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
