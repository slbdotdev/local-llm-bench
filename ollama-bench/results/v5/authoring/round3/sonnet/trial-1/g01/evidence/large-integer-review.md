# Large integer review

Relay does not put a practical bound on a valid integer delta. The export layer
uses Python integers and the reducer performs the same multiplication and
addition for small and large values. The review used values near the size of a
64-bit counter and then deliberately exceeded that size.

For one platform build key, accepted changes were add `10**18`, remove
`-10**18`, adjust `10**18 + 7`, and hold `-10**30`. The total is
`2000000000000000007`, occurrences is four, and all accepted labels are merged
in order. The hold's large raw value is irrelevant to arithmetic but not to
acceptance or occurrence.

A zero-valued remove still increments count and can introduce labels. A pair of
equal and opposite contributions can leave total zero without making the entry
empty. The reducer must not use numeric magnitude, truthiness, or an assumed
machine integer width to decide whether a change exists.

Administrative changes with large values are still rejected. Their values and
labels do not affect a later accepted occurrence. The numeric review is thus
crossed with policy review: arithmetic happens only after acceptance, and
accepted zero arithmetic remains stateful.

The result contains ordinary Python ints. Converting to float, clipping to a
fixed range, or serializing and reparsing during transformation would change
valid values and is not part of the release behavior.
