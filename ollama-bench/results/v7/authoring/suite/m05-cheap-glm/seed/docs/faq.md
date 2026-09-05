# Pricing FAQ

**Why cents?** Floats drift; the card's rounding rule is exact, so the
calculator does all money in integer cents and rounds only where the card
says, always halves up.

**Which weight is "billable"?** The larger of the actual weight and the
volumetric weight, both whole kilograms; R2 of the rate card.

**Do the supplements attract fuel?** No. The fuel line is 12% of the
zone-multiplied base charge alone (R5). Residential, oversize and
Saturday are added after it and are never part of the fuel line.

**What is refused rather than priced?** Returns labels outside zone A
(R8). Everything else has a price in every zone.

**Who owns a pricing dispute?** Client Integrations, per
docs/claims-process.md. The card is authoritative; Compliance Review owns
changes to the card itself.

**Can the calculator be tuned for a one-off customer deal?** No. Special
terms are handled as an invoice adjustment after the fact, never by
bending a rule in the calculator. The next review will not remember a
fudge; the card will not either.

**Why does the calculator take the zone letter rather than the country?**
So that the quoting device and the pricing device agree on the boundary.
The country-to-zone map (zones.py) is an input, not a pricing rule, and
it changes only when the depots re-brief.

**What happens when the card changes?** The review writes the dated
record in history/, the card is updated, and then the calculator is
brought in line - in that order. Between the first two steps the tree is
allowed to disagree with itself on disk; after the third it is not.
