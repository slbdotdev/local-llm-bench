"""Behavioural checks for digest_flow."""

from kestrel.digest_flow import DigestGateway, build_digest


def test_digest_defaults():
    engine = DigestGateway()
    assert engine.limit == 96
    assert engine.window_s == 90


def test_digest_seal_is_idempotent():
    engine = DigestGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestGateway()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
