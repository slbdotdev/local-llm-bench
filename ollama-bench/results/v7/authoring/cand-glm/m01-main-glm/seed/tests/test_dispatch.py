"""Behavioural checks for dispatch_store."""

from cordage.dispatch_store import DispatchRegistry, build_dispatch


def test_dispatch_defaults():
    engine = DispatchRegistry()
    assert engine.limit == 250
    assert engine.window_s == 120


def test_dispatch_seal_is_idempotent():
    engine = DispatchRegistry()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
