Migrate the three application modules and the supplied test so the suite still passes.
Do not change unrelated files.

Rename the public function `join_bits` to `merge_bits`. At the same time, change its
exact signature from:

    join_bits(left, right, glue="-")

to:

    merge_bits(right, left, *, glue="-")

The function's result must not change: the left piece is still written first, then the
glue, then the right piece. Therefore every definition and call site must be updated,
including the default `joiner`, the pair-comprehension (whose two arguments must swap),
the `getattr` string in the view layer, and the executable doctest. All glue arguments
must now be keyword arguments. Preserve the three-module import relationship and run
the supplied test with Python after editing it.

The checker verifies both the exact signature and outputs that distinguish the two
argument orders. It searches only the three application modules for the old name; extra
padding files are irrelevant.
