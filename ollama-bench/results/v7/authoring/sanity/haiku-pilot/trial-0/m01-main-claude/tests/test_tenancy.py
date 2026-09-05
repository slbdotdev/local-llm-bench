"""Behavioural checks for tenancy_core."""

from cinder.tenancy_core import TenancyRegistry, build_tenancy


def test_tenancy_defaults():
    engine = TenancyRegistry()
    assert engine.limit == 250
    assert engine.window_s == 120


def test_tenancy_seal_is_idempotent():
    engine = TenancyRegistry()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyRegistry()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
