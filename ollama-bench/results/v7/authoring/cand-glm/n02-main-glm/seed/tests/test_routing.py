"""Behavioural checks for routing_core."""

from linnet.routing_core import RoutingPlanner, build_routing


def test_routing_defaults():
    engine = RoutingPlanner()
    assert engine.limit == 480
    assert engine.window_s == 45


def test_routing_seal_is_idempotent():
    engine = RoutingPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
