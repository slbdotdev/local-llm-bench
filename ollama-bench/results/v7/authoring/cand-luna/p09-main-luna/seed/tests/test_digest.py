"""Behavioural checks for digest_view."""

from sable.digest_view import DigestPlanner, build_digest


def test_digest_defaults():
    engine = DigestPlanner()
    assert engine.limit == 250
    assert engine.window_s == 30


def test_digest_seal_is_idempotent():
    engine = DigestPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestPlanner()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
