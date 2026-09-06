"""Behavioural checks for dispatch_view."""

from accord.dispatch_view import DispatchPlanner, build_dispatch


def test_dispatch_defaults():
    engine = DispatchPlanner()
    assert engine.limit == 960
    assert engine.window_s == 60


def test_dispatch_seal_is_idempotent():
    engine = DispatchPlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchPlanner()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
