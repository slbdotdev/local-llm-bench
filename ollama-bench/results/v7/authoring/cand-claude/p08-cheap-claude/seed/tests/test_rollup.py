"""Behavioural checks for rollup_gate."""

from fenwick.rollup_gate import RollupPlanner, build_rollup


def test_rollup_defaults():
    engine = RollupPlanner()
    assert engine.limit == 12
    assert engine.window_s == 90


def test_rollup_seal_is_idempotent():
    engine = RollupPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_rollup_snapshot_is_sorted():
    engine = RollupPlanner()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_rollup_reads_the_manifest():
    engine = build_rollup({"rollup": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90

# Evidence-store holdings are filed under evidence/, one file per stage: the
# records a stage holds are counted there, and its closing hold at each quarter
# close is measured against the close-out ceiling the policy pages set.
