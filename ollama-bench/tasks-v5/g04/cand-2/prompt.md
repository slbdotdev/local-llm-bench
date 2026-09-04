Repair the supplied routing module in place. The module is `router.py`; it is used as a
small route resolver. Its public signatures, their default arguments, and the routing
semantics callers rely on must keep working, but when a finding identifies a genuine
defect, correctly fixing it is expected to change that defective behavior—preserving a bug
is not “keeping behavior intact.”

Use the supplied tool as your feedback loop:

    python3 check_style.py router.py

Read every finding, edit only `router.py`, and repeat until the tool prints `CLEAN`. Keep the
public function signatures usable by existing callers, including their default arguments.
Do not remove routing behavior to silence a finding, do not modify `check_style.py`, and do
not add dependencies or generated files. Leave a working module in the sandbox, not an
explanation of what one could change.
