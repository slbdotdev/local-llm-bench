"""Behavioural checks for drain_view."""

from CedarSignal.drain_view import DrainGateway, build_drain


def test_drain_defaults():
    engine = DrainGateway()
    assert engine.limit == 250
    assert engine.window_s == 120


def test_drain_seal_is_idempotent():
    engine = DrainGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_drain_snapshot_is_sorted():
    engine = DrainGateway()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_drain_reads_the_manifest():
    engine = build_drain({"drain": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
