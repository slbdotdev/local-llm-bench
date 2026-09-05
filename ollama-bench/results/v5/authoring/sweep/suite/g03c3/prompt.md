Migrate the three application modules and the supplied test so the suite still passes.
Do not change unrelated files.

Rename the public function `emit_note` to `write_note`. Its new exact signature is:

    write_note(message, *, channel="log", urgent=False)

The normal output remains `channel:message`. When `urgent=True`, prefix it with
`URGENT `. Every function that forwards a call—including the function that dispatches
reflectively—must accept and pass through the new keyword-only `channel` and `urgent`
options. Update every
definition and call site, including the default `sender`, the list comprehension, the
string used by `getattr`, and the executable doctest. Calls must use keywords for
`channel` and `urgent`; preserve the three-module import relationship.

Run the supplied test with Python. The checker searches only the three application
modules for the old name, and it exercises both the default (non-urgent) and explicit
urgent paths. Extra padding files are irrelevant.
