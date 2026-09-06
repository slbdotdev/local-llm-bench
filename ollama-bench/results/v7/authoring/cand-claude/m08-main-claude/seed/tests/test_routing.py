"""Behavioural checks for routing_gate."""

from cordage.routing_gate import RoutingRegistry, build_routing


def test_routing_defaults():
    engine = RoutingRegistry()
    assert engine.limit == 48
    assert engine.window_s == 30


def test_routing_seal_is_idempotent():
    engine = RoutingRegistry()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_routing_snapshot_is_sorted():
    engine = RoutingRegistry()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_routing_reads_the_manifest():
    engine = build_routing({"routing": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
