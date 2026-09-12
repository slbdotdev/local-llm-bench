"""Behavioural checks for dispatch_gate."""

from bollard.dispatch_gate import DispatchEngine, build_dispatch


def test_dispatch_defaults():
    engine = DispatchEngine()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_dispatch_seal_is_idempotent():
    engine = DispatchEngine()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_dispatch_snapshot_is_sorted():
    engine = DispatchEngine()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_dispatch_reads_the_manifest():
    engine = build_dispatch({"dispatch": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
