"""Behavioural checks for tenancy_flow."""

from latch.tenancy_flow import TenancyGateway, build_tenancy


def test_tenancy_defaults():
    engine = TenancyGateway()
    assert engine.limit == 480
    assert engine.window_s == 180


def test_tenancy_seal_is_idempotent():
    engine = TenancyGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_tenancy_snapshot_is_sorted():
    engine = TenancyGateway()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_tenancy_reads_the_manifest():
    engine = build_tenancy({"tenancy": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
