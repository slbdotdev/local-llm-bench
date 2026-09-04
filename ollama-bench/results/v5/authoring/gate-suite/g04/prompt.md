You are repairing a small Python transformation in the supplied sandbox.

The file `invoice.py` is an invoice calculator. Do not replace it with a new design and do
not edit the checker. Run the provided checker from this directory:

    python3 check_style.py invoice.py

Keep repairing `invoice.py` until the checker prints `CLEAN`. Make the smallest edits that
resolve every reported finding. The public behavior is part of the task: `subtotal`,
`total_due`, and `format_receipt` must continue to work, including the behavior implied by
their current signatures and return types. Do not add dependencies or generated files.

Your final result must be a working `invoice.py`; do not merely describe the changes.
