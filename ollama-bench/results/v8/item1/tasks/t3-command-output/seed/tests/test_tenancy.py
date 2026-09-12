"""Behavioural checks for tenancy_gate."""

from capstan.tenancy_gate import TenancyRegistry, build_tenancy


def test_tenancy_defaults():
    engine = TenancyRegistry()
    assert engine.limit == 96
    assert engine.window_s == 180


def test_tenancy_seal_is_idempotent():
    engine = TenancyRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyRegistry()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
