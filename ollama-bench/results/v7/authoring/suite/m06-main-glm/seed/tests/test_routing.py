"""Behavioural checks for routing_gate."""

from larkspur.routing_gate import RoutingGateway, build_routing


def test_routing_defaults():
    engine = RoutingGateway()
    assert engine.limit == 12
    assert engine.window_s == 60


def test_routing_seal_is_idempotent():
    engine = RoutingGateway()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
