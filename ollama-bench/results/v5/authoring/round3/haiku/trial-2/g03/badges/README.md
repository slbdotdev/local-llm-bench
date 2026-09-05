# Badge application package

The Python package in this directory is a deliberately ordinary application
tree: core construction feeds a registry and flow layer, then services,
plugins, workflows, reports, and adapters consume the result.  The public
builder is used directly, retained as a callable, passed through a registry,
and exercised by the supplied tests.

The README is context for maintainers and is not executable source.  It names
the historical API because release notes and source comments often do too.
The migration request applies to Python definitions, calls, reflected names,
and the supplied test, not prose documentation.
