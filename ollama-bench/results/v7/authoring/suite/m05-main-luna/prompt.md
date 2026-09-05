# Reconcile the admission policy documentation

A small handoff-admission policy has drifted: its documentation and implementation disagree.
Locate the matching implementation and its documentation by reading the repository. Update the
documentation so it accurately describes the implementation's defaults and lifecycle states.

When documentation and code conflict, the code is authoritative for this task. The implementation
is already correct and must not be changed. Edit only the documentation: do not modify the Python
implementation, tests, manifest, generated project files, or any other file. Preserve the existing
style and explanatory text; correct the documented `limit`, `window_s`, and state name so they match
the implementation exactly. Keep the lifecycle states listed in the order used by the code.
