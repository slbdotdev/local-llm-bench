"""Behavioural checks for dispatch_store."""

from emberledger_core.dispatch_store import DispatchPlanner, build_dispatch


def test_dispatch_defaults():
    engine = DispatchPlanner()
    assert engine.limit == 32
    assert engine.window_s == 15


def test_dispatch_seal_is_idempotent():
    engine = DispatchPlanner()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchPlanner()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
