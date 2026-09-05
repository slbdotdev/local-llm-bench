"""Behavioural checks for digest_store."""

from cinder.digest_store import DigestLedger, build_digest


def test_digest_defaults():
    engine = DigestLedger()
    assert engine.limit == 250
    assert engine.window_s == 15


def test_digest_seal_is_idempotent():
    engine = DigestLedger()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestLedger()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
