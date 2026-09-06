"""Behavioural checks for tenancy_gate."""

from opaltelemetry.tenancy_gate import TenancyRegistry, build_tenancy


def test_tenancy_defaults():
    engine = TenancyRegistry()
    assert engine.limit == 960
    assert engine.window_s == 30


def test_tenancy_seal_is_idempotent():
    engine = TenancyRegistry()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyRegistry()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
