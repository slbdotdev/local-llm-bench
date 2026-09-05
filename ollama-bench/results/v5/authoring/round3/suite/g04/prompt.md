You are repairing a Python reconciliation transformation in the supplied sandbox.

The project is a ledger close with a large set of processor feeds. Read the project guide,
the current policy and output-contract memos, the archived policy/history notes, the
currency and account tables, every region feed under \`data/\`, and the supplied
\`src/reconcile.py\` before editing. The archived notes are context, not current authority.

Repair \`src/reconcile.py\` in place. Do not replace it with a new design, do not edit the
feeds, documentation, or checker, and do not add dependencies or generated files. Preserve
the public signatures and return types of \`reconcile()\` and \`format_report()\`. The current
policy is authoritative for the 2025-12-31 close, including which rows count, how fees and
currency conversion are calculated, how accounts and tax codes are grouped, and the exact
ordering of output.

Run the supplied checker from the project root:

    python3 check_project.py

Keep repairing \`src/reconcile.py\` until it prints \`CLEAN\`. Make the smallest edits that
resolve every reported finding while preserving the specified behavior. Your final result
must be the working source file, not a description of changes.
