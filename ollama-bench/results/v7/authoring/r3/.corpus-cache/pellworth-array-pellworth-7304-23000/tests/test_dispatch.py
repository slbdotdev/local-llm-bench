"""Behavioural checks for dispatch_store."""

from pellworth.dispatch_store import DispatchEngine, build_dispatch


def test_dispatch_defaults():
    engine = DispatchEngine()
    assert engine.limit == 48
    assert engine.window_s == 60


def test_dispatch_seal_is_idempotent():
    engine = DispatchEngine()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchEngine()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
