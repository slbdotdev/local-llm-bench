"""Behaviour the rate arithmetic has to have. See docs/rounding.md."""
from ledger.rates import invoice_total, line_total, round_half_up


def test_round_half_up_rounds_half_away_from_zero():
    assert round_half_up(0.4) == 0
    assert round_half_up(0.5) == 1
    assert round_half_up(1.5) == 2
    assert round_half_up(2.5) == 3
    assert round_half_up(3.5) == 4


def test_round_half_up_leaves_whole_cents_alone():
    assert round_half_up(0.0) == 0
    assert round_half_up(7.0) == 7


def test_line_total_uses_the_rate_table():
    assert line_total("storage", 1000) == 4
    assert line_total("lookup", 1000) == 190


def test_line_total_rounds_the_half_cent_up():
    # 37 * 500 / 1000 = 18.5 cents
    assert line_total("transit", 500) == 19


def test_invoice_total_rounds_each_line_before_summing():
    assert invoice_total([("transit", 500), ("transit", 500)]) == 38
