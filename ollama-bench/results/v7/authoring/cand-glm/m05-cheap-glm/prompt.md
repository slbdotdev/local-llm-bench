# Make the rate calculator match the rate card

Kestrel Courier prices parcels with `src/kestrel/rates.py`. The company's
rate card, `docs/rate-card.md`, is the single source of truth for pricing:
**where the code and the card disagree, the card is authoritative and the
code is what must be fixed.** Changing the card, or any other document, so
that it agrees with the code is the one direction this must never go.

## Your task

1. Read the rate card and the calculator, rule by rule, and find every
   point where `rates.py` does not implement the card.
2. Fix `src/kestrel/rates.py` so that `quote()` implements every rule
   R1-R8 exactly as the card states it, and `returns_label()` implements
   R8. Keep `quote()` and `returns_label()` exactly as they are in name,
   parameter order and return type; everything else inside `rates.py` is
   yours to change.
3. Create `fixlog.txt` in the repository root (next to README.md)
   listing all eight rules, one per line, in ascending rule order, with no
   header and no other text. Each line is either `R<n> MATCHES` (the code
   already agreed with the card) or `R<n> CORRECTED` (you had to change
   the code to agree). Attribute a correction to the rule whose own
   statement the code got wrong: a rule counts as `CORRECTED` only if you
   changed the code that implements **that rule's own statement**, and a
   rule whose computed result changes only as a consequence of correcting
   a different rule still counts as `MATCHES`. For illustration only, if R3 and R7 had been the
   only disagreements, the file would read exactly:

       R1 MATCHES
       R2 MATCHES
       R3 CORRECTED
       R4 MATCHES
       R5 MATCHES
       R6 MATCHES
       R7 CORRECTED
       R8 MATCHES

   That example is illustrative only; it is not this card's answer.

## Scope

The only existing file you may modify is `src/kestrel/rates.py`, plus the
new `fixlog.txt`. Everything else - the rate card, the notes, the tests,
the samples, every other existing file - must stay exactly as it is.
