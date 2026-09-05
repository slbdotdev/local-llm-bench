Update the three application modules and their supplied test so the test suite still
passes. Do not modify unrelated files.

This is a coordinated API migration. In the application modules, rename the public
function `emit_event` to `publish_event`. Its new exact signature is:

    publish_event(payload, kind, *, channel="main", stamped=False)

The returned text keeps the old presentation order: `channel|kind|payload`.
When `stamped=True`, prefix that complete text with `STAMP `. When it is false,
do not add a prefix. The public function's two data arguments have deliberately
swapped positions, but the displayed kind must still precede the payload.

Update every definition and every call site. This includes the default `sender`,
the pair comprehension in the batch helper (whose arguments must swap), the
reflective `getattr` string, the fallback used by reflection, and the executable
doctest. Every forwarding function must accept and pass through `channel` and
`stamped`; those two options are keyword-only wherever they are accepted. All
calls supplying either option must use keywords. Do not leave a compatibility
alias or the old spelling in any of the three application modules.

The supplied test is part of the migration: update its calls and run it with
Python after editing it. Preserve the three-module import relationship. The
checker exercises asymmetric kind/payload values, default and stamped paths,
the batch comprehension, reflection, the exact signature, and rejection of
the old positional form. It searches only the three application modules for
the old name; extra padding files are irrelevant.
