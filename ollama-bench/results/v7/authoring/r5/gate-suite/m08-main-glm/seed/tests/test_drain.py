"""Behavioural checks for drain_gate."""

from emberledger_core.drain_gate import DrainRegistry, build_drain


def test_drain_defaults():
    engine = DrainRegistry()
    assert engine.limit == 24
    assert engine.window_s == 45


def test_drain_seal_is_idempotent():
    engine = DrainRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainRegistry()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
