"""Behavioural checks for dispatch_view."""

from kestrel.dispatch_view import DispatchLedger, build_dispatch


def test_dispatch_defaults():
    engine = DispatchLedger()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_dispatch_seal_is_idempotent():
    engine = DispatchLedger()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchLedger()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
