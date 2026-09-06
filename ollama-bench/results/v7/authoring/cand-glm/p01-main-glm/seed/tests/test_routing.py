"""Behavioural checks for routing_core."""

from quay.routing_core import RoutingRegistry, build_routing


def test_routing_defaults():
    engine = RoutingRegistry()
    assert engine.limit == 64
    assert engine.window_s == 60


def test_routing_seal_is_idempotent():
    engine = RoutingRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
