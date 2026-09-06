"""Behavioural checks for drain_core."""

from ember.drain_core import DrainPlanner, build_drain


def test_drain_defaults():
    engine = DrainPlanner()
    assert engine.limit == 64
    assert engine.window_s == 30


def test_drain_seal_is_idempotent():
    engine = DrainPlanner()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainPlanner()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
