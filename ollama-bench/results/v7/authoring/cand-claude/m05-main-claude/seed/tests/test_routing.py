"""Behavioural checks for routing_flow."""

from hearth.routing_flow import RoutingPlanner, build_routing


def test_routing_defaults():
    engine = RoutingPlanner()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_routing_seal_is_idempotent():
    engine = RoutingPlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingPlanner()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
