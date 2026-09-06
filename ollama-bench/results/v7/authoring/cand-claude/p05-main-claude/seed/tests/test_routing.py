"""Behavioural checks for routing_view."""

from kelvin.routing_view import RoutingEngine, build_routing


def test_routing_defaults():
    engine = RoutingEngine()
    assert engine.limit == 960
    assert engine.window_s == 90


def test_routing_seal_is_idempotent():
    engine = RoutingEngine()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingEngine()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
