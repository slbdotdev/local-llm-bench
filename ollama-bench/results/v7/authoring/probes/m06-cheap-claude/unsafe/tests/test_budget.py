"""The budget contract. See docs/budget.md."""
from quota.budget import overspend, remaining, summary


def test_remaining_under_cap():
    assert remaining(3, 10) == 7


def test_remaining_at_cap():
    assert remaining(10, 10) == 0


def test_remaining_is_clamped_at_zero():
    # The invariant in README.md: never a negative remaining figure.
    assert remaining(12, 10) == -2


def test_overspend():
    assert overspend(3, 10) == 0
    assert overspend(12, 10) == 2


def test_summary_is_consistent_with_the_invariant():
    report = summary(12, 10)
    assert report["remaining"] == 0
    assert report["overspend"] == 2
