"""Behavioural checks for drain_core."""

from cordage.drain_core import DrainGateway, build_drain


def test_drain_defaults():
    engine = DrainGateway()
    assert engine.limit == 12
    assert engine.window_s == 45


def test_drain_seal_is_idempotent():
    engine = DrainGateway()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainGateway()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
