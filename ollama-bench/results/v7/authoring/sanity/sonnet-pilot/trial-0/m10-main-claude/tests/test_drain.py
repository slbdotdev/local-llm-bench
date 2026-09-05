"""Behavioural checks for drain_gate."""

from thistle.drain_gate import DrainPlanner, build_drain


def test_drain_defaults():
    engine = DrainPlanner()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_drain_seal_is_idempotent():
    engine = DrainPlanner()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
