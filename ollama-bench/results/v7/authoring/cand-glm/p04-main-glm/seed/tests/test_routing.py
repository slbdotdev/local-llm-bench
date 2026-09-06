"""Behavioural checks for routing_flow."""

from latch.routing_flow import RoutingLedger, build_routing


def test_routing_defaults():
    engine = RoutingLedger()
    assert engine.limit == 12
    assert engine.window_s == 45


def test_routing_seal_is_idempotent():
    engine = RoutingLedger()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingLedger()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
