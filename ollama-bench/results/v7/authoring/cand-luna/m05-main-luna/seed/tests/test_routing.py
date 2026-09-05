"""Behavioural checks for routing_gate."""

from CedarSignal.routing_gate import RoutingGateway, build_routing


def test_routing_defaults():
    engine = RoutingGateway()
    assert engine.limit == 960
    assert engine.window_s == 30


def test_routing_seal_is_idempotent():
    engine = RoutingGateway()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingGateway()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
