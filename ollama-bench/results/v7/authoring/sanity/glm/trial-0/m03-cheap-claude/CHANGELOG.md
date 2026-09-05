# Changelog

## 2034-02-11
- `normalise.kind_of` lower-cases before looking up an alias; the meter changed casing in
  firmware 4.2 and the alias table stopped matching.

## 2034-01-28
- `docs/rounding.md` written down properly after the quarterly discrepancy. The rule was always
  half-up; it had never been stated anywhere a reader would find it.

## 2033-12-03
- `invoice_total` rounds each line before summing rather than summing and rounding once. The
  difference is real and the per-line form is what the contracts say.
