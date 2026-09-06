"""Behavioural checks for routing_flow."""

from vantage.routing_flow import RoutingLedger, build_routing


def test_routing_defaults():
    engine = RoutingLedger()
    assert engine.limit == 120
    assert engine.window_s == 90


def test_routing_seal_is_idempotent():
    engine = RoutingLedger()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingLedger()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
