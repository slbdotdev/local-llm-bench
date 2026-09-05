# Handover notes - pricing

*(H. Bergstrom, last day 2026-09-12.)*

Things the next person will want to know, in no particular order:

- The September rate card (docs/rate-card.md) is effective 2026-09-01 and
  is the pricing authority. Company policy here is old and simple: the
  card wins, the calculator follows. If anyone ever asks you to "just
  change the card to match the code", that is a Compliance Review
  decision, not an engineering one.
- The calculator (src/kestrel/rates.py) is ordinary integer-cents Python.
  There are deliberately no tests pinning the rate rules: when the card
  changed under a pinned test last spring, the suite went red for a week
  while the card was still being drafted. The card is the specification;
  the way to check the code against it is to read both side by side.
- Zone letters come from zones.py; the mapping is stable and agreed with
  the depots. A pricing problem is never fixed by renumbering zones; the
  fix belongs in the card first and then in the calculator.
- The depot teams sanity-check a disputed price against the card's worked
  examples, so the examples matter as much as the rules.
