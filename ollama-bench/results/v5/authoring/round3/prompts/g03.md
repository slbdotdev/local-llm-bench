Perform the public API migration in this application tree. Work from the supplied Python
package and its supplied integration test; inspect the whole package, including its
subpackages, before editing. Run the supplied test with Python when you are done.

In every Python application module, rename the public function `make_tag` to `make_badge`.
The new definition in the core module must have exactly this interface:

    make_badge(label, *, tone="plain")

Update every definition, import, call site, retained callable, default argument, dispatch
table, registry lookup, reflected string, comprehension, lambda, and executable doctest that
refers to the old public name. The old identifier and its reflected string must not remain in
the Python application source. Calls that provide a tone must pass it by the keyword `tone`;
the old positional form is invalid. Calls that omit it must keep the default behavior.

Preserve every observable output, the package's import relationships, and the existing order
of definitions and executable statements. Do not reorder existing test assertions or
application statements. Do not change prose documentation or unrelated non-Python files.
Do not add dependencies, network access, or generated artifacts. The final tree must remain
usable with standard-library Python from its root, and the supplied test must still pass.
