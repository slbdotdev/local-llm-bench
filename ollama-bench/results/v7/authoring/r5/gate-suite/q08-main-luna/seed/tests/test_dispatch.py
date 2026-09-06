"""Behavioural checks for dispatch_core."""

from orison.dispatch_core import DispatchGateway, build_dispatch


def test_dispatch_defaults():
    engine = DispatchGateway()
    assert engine.limit == 64
    assert engine.window_s == 30


def test_dispatch_seal_is_idempotent():
    engine = DispatchGateway()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchGateway()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
