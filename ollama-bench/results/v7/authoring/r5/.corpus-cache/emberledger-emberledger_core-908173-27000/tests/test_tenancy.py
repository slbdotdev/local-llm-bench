"""Behavioural checks for tenancy_gate."""

from emberledger_core.tenancy_gate import TenancyPlanner, build_tenancy


def test_tenancy_defaults():
    engine = TenancyPlanner()
    assert engine.limit == 32
    assert engine.window_s == 60


def test_tenancy_seal_is_idempotent():
    engine = TenancyPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyPlanner()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
