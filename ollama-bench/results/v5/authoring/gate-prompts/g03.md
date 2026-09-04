Update the three application modules in this directory and their supplied test so the
test suite still passes. Do not modify unrelated files.

This is a mechanical API migration. In the application modules, rename the public
function `make_tag` to `make_badge`. Its new exact signature is:

    make_badge(label, *, tone="plain")

Update every definition and every call site, including references held by a default
argument, the string passed to `getattr`, the call inside the list comprehension, and
the executable doctest example. Preserve the existing outputs and the import relationship
between the three modules. Calls that need the second argument must now pass `tone` by
keyword; the old positional form is no longer valid.

The supplied test is part of the migration: update its calls and run it with Python.
The checker also searches the three application modules for the old name, so a leftover
identifier or reflected string is not acceptable. It ignores unrelated padding files.
