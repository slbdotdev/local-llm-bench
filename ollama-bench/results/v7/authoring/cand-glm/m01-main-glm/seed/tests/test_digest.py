"""Behavioural checks for digest_store."""

from cordage.digest_store import DigestGateway, build_digest


def test_digest_defaults():
    engine = DigestGateway()
    assert engine.limit == 12
    assert engine.window_s == 45


def test_digest_seal_is_idempotent():
    engine = DigestGateway()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
