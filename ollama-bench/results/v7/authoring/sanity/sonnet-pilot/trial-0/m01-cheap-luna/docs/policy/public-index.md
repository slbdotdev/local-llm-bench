# Public index policy

This policy applies to the schema stage's externally consumed index and is maintained here
because the index is also used by the overnight catalog publisher.

When the schema stage publishes its snapshot, enumerate the keys from the greatest string to
the least string; the ascending convention remains in force for every other stage.

The publisher consumes records after the stage has been sealed. It does not reinterpret keys,
rename them, or apply a locale-specific collation. A stable ordinary string comparison is the
comparison intended by this policy.
