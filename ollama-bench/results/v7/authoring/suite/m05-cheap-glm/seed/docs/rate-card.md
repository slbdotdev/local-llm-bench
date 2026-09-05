# Kestrel Courier - rate card

**Effective 2026-09-01. This card is the single source of truth for
quoting. Where the calculator and this card disagree, the card is
authoritative and the calculator is to be corrected.**

All amounts are euros. The calculator works in integer cents, and every
rule below that can produce a fraction of a cent says how to round:
rounded to the nearest cent, halves rounded up.

## R1 - base charge by billable weight

Billable weight is a whole number of kilograms (R2 decides it).

- up to and including 1 kg: 6.00
- over 1 kg up to and including 5 kg: 6.00 plus 1.80 for each whole
  kilogram over 1
- over 5 kg: 13.20 plus 1.10 for each whole kilogram over 5

Worked weights: 1 kg -> 6.00; 3 kg -> 9.60; 5 kg -> 13.20; 10 kg -> 18.70;
12 kg -> 20.90.

## R2 - billable weight

The volumetric weight of a parcel is its length x width x height in
centimetres divided by 5000, **rounded up to the next whole kilogram**
(a result that is already a whole number stays as it is). Billable weight
is the larger of the actual weight and the volumetric weight. Actual
weight is given in whole kilograms.

## R3 - zone multiplier

The base charge is multiplied by the zone factor and rounded to the
nearest cent, halves up:

| zone | factor |
| ---- | ------ |
| A    | 1.00   |
| B    | 1.15   |
| C    | 1.30   |
| D    | 1.55   |

## R4 - residential supplement

Deliveries to a residential address carry a flat 4.50 supplement. The
supplement is not zone-multiplied and does not attract fuel surcharge; it
is added after the fuel line.

## R5 - fuel surcharge

12% of the zone-multiplied base charge (R3), rounded to the nearest cent,
halves up. The fuel line is computed on the zone-multiplied base charge
alone: the residential, oversize and Saturday amounts are never part of
it.

## R6 - Saturday delivery

A requested Saturday delivery adds a flat 9.00 after everything else. It
does not attract fuel surcharge.

## R7 - oversize supplement

A parcel whose billable weight is over 25 kg adds a flat 14.00. Like the
residential and Saturday amounts it is added after the fuel line and does
not attract fuel.

## R8 - returns label

A returns label is a flat 5.80 and is sold for zone A only. No zone
multiplier, no fuel and no supplements apply to it. A returns label asked
for any other zone must be refused: the calculator raises an error rather
than quoting a price.

## Worked examples

Both examples are zone A, so R3 leaves the base charge alone.

1. An 8 kg parcel, 30 x 20 x 10 cm, zone A, business address, no Saturday:
   billable weight 8 kg, base 16.50, fuel 1.98, total **18.48**.
2. A 4 kg parcel, 25 x 15 x 12 cm, zone A, business address, Saturday
   delivery requested: billable weight 4 kg, base 11.40, fuel 1.37,
   Saturday 9.00, total **21.77**.
