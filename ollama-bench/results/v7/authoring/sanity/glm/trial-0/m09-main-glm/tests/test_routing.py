"""Behavioural checks for routing_gate."""

from cinder.routing_gate import RoutingPlanner, build_routing


def test_routing_defaults():
    engine = RoutingPlanner()
    assert engine.limit == 32
    assert engine.window_s == 90


def test_routing_seal_is_idempotent():
    engine = RoutingPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingPlanner()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
