"""Behavioural checks for drain_store."""

from dogvane.drain_store import DrainRegistry, build_drain


def test_drain_defaults():
    engine = DrainRegistry()
    assert engine.limit == 48
    assert engine.window_s == 120


def test_drain_seal_is_idempotent():
    engine = DrainRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
