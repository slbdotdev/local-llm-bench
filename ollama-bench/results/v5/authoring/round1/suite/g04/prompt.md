Repair the supplied authorization-policy module in place. The target is `policy.py`; it is a
small rule resolver used by an application. Preserve its public functions, signatures, and
the behavior encoded by the existing implementation, including rule order and the handling
of absent fields. When the checker identifies a genuine defect, fix it rather than deleting
the behavior that exposed it.

Use the supplied checker as your feedback loop:

    python3 check_style.py policy.py

Read every finding, edit only `policy.py`, and repeat until the command prints `CLEAN`. Keep
the repair minimal and standard-library-only. Do not modify `check_style.py`, add generated
files or dependencies, or merely describe a proposed patch. Finish with a working
`policy.py` in the sandbox.
