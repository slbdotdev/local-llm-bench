# kestrel

Quote calculator for Kestrel Courier parcels: what a parcel costs to move,
rule by rule, in integer euro cents. No floats anywhere in the money
arithmetic.

## The rate card is the law

`docs/rate-card.md` is the company's single source of truth for pricing.
Company policy, restated in `docs/handover-notes.md`, is that **where the
calculator and the card disagree, the card wins**: the code is corrected,
never the card.

## Layout

    src/kestrel/         the package
        rates.py         the quote calculator (one parcel, integer cents)
        zones.py         country-to-zone mapping
    tests/               pytest-style tests
    docs/                rate card, handover notes, claims process, FAQ
    history/             pricing decision records
    samples/             consignments the depots actually quoted in September

## Running

    python -m pytest tests/test_zones.py

The zone tests pass on the current code. The rate rules themselves are not
pinned by tests; the rate card is their specification, and the way to check
the code against the card is to read both (see the handover notes for why
there is no rates test).
