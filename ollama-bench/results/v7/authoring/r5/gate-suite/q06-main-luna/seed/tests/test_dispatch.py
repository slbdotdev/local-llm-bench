"""Behavioural checks for dispatch_core."""

from opaltelemetry.dispatch_core import DispatchRegistry, build_dispatch


def test_dispatch_defaults():
    engine = DispatchRegistry()
    assert engine.limit == 96
    assert engine.window_s == 15


def test_dispatch_seal_is_idempotent():
    engine = DispatchRegistry()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchRegistry()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
