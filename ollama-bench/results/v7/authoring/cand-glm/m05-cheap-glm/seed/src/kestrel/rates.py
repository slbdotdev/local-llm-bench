"""kestrel.rates: price one Kestrel Courier parcel in integer euro cents.

The specification is docs/rate-card.md; this module is the implementation.
quote() takes a parcel's physical figures and returns the price in cents.
returns_label() prices a returns label. All money is integer cents; never
floats.
"""
from __future__ import annotations

BASE_CENTS = 600
BAND2_PER_KG = 180          # per whole kg over 1, up to and including 5
BAND3_PER_KG = 110          # per whole kg over 5
BAND2_TOP = 5
VOLUMETRIC_DIVISOR = 6000
ZONE_MULT_PERCENT = {"A": 100, "B": 115, "C": 130, "D": 155}
FUEL_PERCENT = 12
RESIDENTIAL_CENTS = 450
SATURDAY_CENTS = 900
OVERSIZE_KG = 25
OVERSIZE_CENTS = 1400
RETURNS_LABEL_CENTS = 580


def _round_half_up(cents):
    """Round a whole-or-fractional cent figure to the nearest cent, .5 up."""
    return (cents + 50) // 100


def _volumetric_kg(length_cm, width_cm, height_cm):
    return (length_cm * width_cm * height_cm + VOLUMETRIC_DIVISOR - 1) \
        // VOLUMETRIC_DIVISOR


def _base_cents(billable_kg):
    if billable_kg <= 1:
        return BASE_CENTS
    if billable_kg <= BAND2_TOP:
        return BASE_CENTS + BAND2_PER_KG * (billable_kg - 1)
    return 4 * BAND2_PER_KG + BASE_CENTS + BAND3_PER_KG * (billable_kg - 5)


def quote(weight_kg, length_cm, width_cm, height_cm, zone, residential,
          saturday):
    """Price one parcel; returns integer euro cents. See docs/rate-card.md."""
    billable = max(int(weight_kg), _volumetric_kg(length_cm, width_cm,
                                                  height_cm))
    base = _base_cents(billable)
    zoned = _round_half_up(base * ZONE_MULT_PERCENT[zone])
    fuel_base = zoned
    if residential:
        fuel_base += RESIDENTIAL_CENTS
    if billable > OVERSIZE_KG:
        fuel_base += OVERSIZE_CENTS
    fuel = _round_half_up(fuel_base * FUEL_PERCENT)
    total = zoned + fuel
    if residential:
        total += RESIDENTIAL_CENTS
    if billable > OVERSIZE_KG:
        total += OVERSIZE_CENTS
    if saturday:
        total += SATURDAY_CENTS
    return total


def returns_label(zone):
    """Price a returns label: flat, zone A only (rate card R8)."""
    if zone != "A":
        raise ValueError("returns labels are sold for zone A only "
                         "(rate card R8)")
    return RETURNS_LABEL_CENTS
