"""Behavioural checks for digest_view."""

from pellworth.digest_view import DigestEngine, build_digest


def test_digest_defaults():
    engine = DigestEngine()
    assert engine.limit == 48
    assert engine.window_s == 60


def test_digest_seal_is_idempotent():
    engine = DigestEngine()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestEngine()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
