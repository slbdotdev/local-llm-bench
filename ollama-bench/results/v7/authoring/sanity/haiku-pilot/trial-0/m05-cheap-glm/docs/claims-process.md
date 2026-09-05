# Claims process - overcharged parcels

Owner: Client Integrations.

1. The claimant quotes the parcel figures and the price they were charged.
2. The depot recomputes the price from the rate card rules (R1-R8) for
   those parcel facts, in integer cents, with the rounding the card
   states.
3. If the recompute and the charge differ, the difference is refunded;
   the calculator is then checked against the card, because a refund
   without a fix repeats within the month.
4. Claims older than the current card's effective date are settled on the
   card that was in force, which is why superseded cards are kept under
   history/.

Common causes in 2026 so far, most frequent first: wrong zone letter from
the depot manifest; residential flag missing on the label; billable
weight taken from the nearest kilogram instead of rounded up, which R2
does not allow.
