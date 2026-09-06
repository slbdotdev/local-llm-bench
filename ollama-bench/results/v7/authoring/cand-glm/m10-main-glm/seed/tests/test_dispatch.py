"""Behavioural checks for dispatch_flow."""

from solder.dispatch_flow import DispatchEngine, build_dispatch


def test_dispatch_defaults():
    engine = DispatchEngine()
    assert engine.limit == 96
    assert engine.window_s == 45


def test_dispatch_seal_is_idempotent():
    engine = DispatchEngine()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchEngine()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
