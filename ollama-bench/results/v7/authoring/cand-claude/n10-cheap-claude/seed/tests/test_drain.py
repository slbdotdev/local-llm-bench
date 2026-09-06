"""Behavioural checks for drain_core."""

from arbor.drain_core import DrainEngine, build_drain


def test_drain_defaults():
    engine = DrainEngine()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_drain_seal_is_idempotent():
    engine = DrainEngine()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainEngine()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
