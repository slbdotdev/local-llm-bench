"""Behavioural checks for dispatch_core."""

from harrow.dispatch_core import DispatchPlanner, build_dispatch


def test_dispatch_defaults():
    engine = DispatchPlanner()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_dispatch_seal_is_idempotent():
    engine = DispatchPlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchPlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
