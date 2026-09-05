# 2023 migration memo (archived)

During the first migration, `posted` and `captured` were both accepted.  Refunds were
represented with a negative amount, while chargebacks were represented as a separate
negative fee.  The conversion table was applied to the total after grouping by source
currency.  Those conventions created reconciliation drift and were retired before the
2025 close.

The migration also treated a row dated on the close date as late until the following
day.  This exception was removed when timestamps were normalized to ISO dates.
