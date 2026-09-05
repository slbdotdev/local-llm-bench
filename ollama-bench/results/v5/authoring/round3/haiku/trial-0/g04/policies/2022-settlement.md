# 2022 settlement memo (archived)

The first settlement service accepted any row that was not marked `void`.  It used the
daily average currency table and rounded only after a day was summed.  A dispute was
excluded while open and restored when the merchant won.  This memo applied to the
2022 feed only; it is retained to explain old audit exports and is not the 2025 rule.

The old service grouped aliases by the spelling received from the processor.  Thus
`acme-eu` and `acme` were separate rows in old reports.  That behavior was removed in
the account migration.  Do not use this memo for the current close.
