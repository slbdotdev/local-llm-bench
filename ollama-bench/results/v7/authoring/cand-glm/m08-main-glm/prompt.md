Read the repository's written material and reconcile its sealed records. The repository is your complete source of truth; do not infer a missing rule and do not use assembler-generated summaries as evidence.

Create exactly one UTF-8 text file at `reconciliation.txt` in the repository root. Do not create any other file and do not modify any existing file. Its six non-empty lines must use these keys in exactly this order, with one decimal integer after each colon:

opening
checkpoint_05
checkpoint_10
checkpoint_15
checkpoint_20
final

The value for `opening` is the stated opening figure. The four checkpoints are the running state after 5, 10, 15, and 20 linked records; `final` repeats the state after record 20.

Read all relevant repository material before calculating. Find the written reconciliation procedure, then follow its complete instructions: use the sealed record links to determine order, retrieve both figures associated with each linked record from its evidence material, and apply the stated transition successively. The printed row order is not execution order. Preserve the repository and verify your six numbers before finishing.
