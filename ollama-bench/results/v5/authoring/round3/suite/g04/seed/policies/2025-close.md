# Current 2025 close policy

This memo is authoritative for the close dated 2025-12-31.

1. Read every region feed.  Keep a row only when `state` is exactly `posted`,
   `posted_on` is on or before `2025-12-31`, and `voided` is false.
2. A row with `dispute` equal to `lost` is excluded.  `none`, `open`, and `won` are
   included.  The `kind` field is already signed by the feed: a refund's gross amount
   is negative and must not be negated again.
3. Compute `gross_cents - fee_cents` in the row's native currency.  Convert that amount
   with `data.rates.RATES_TO_USD`, then round that row to two decimal places using
   Decimal `ROUND_HALF_UP`.  Sum the rounded rows, not the unrounded rows.
4. Replace `account` with `data.accounts.ACCOUNT_ALIASES[account]`.  Totals are grouped
   by that canonical account.  Unknown aliases are an input error and must not be
   silently assigned to a new account.
5. Group accepted rows by `tax_code` as well as by account.  A report's account keys and
   tax-code keys are sorted lexicographically.  Within `accepted_ids`, sort by
   `(posted_on, entry_id)`.
6. The returned dictionary has exactly these keys: `total_usd`, `by_account`,
   `by_tax_code`, `accepted_ids`, and `accepted_count`.  Decimal values are quantized to
   `0.01`.  `format_report()` prints the same values without changing their precision.

The feed's `posted_on` values are ISO `YYYY-MM-DD` strings, so their lexical ordering is
the date ordering.  No timezone conversion is involved.
