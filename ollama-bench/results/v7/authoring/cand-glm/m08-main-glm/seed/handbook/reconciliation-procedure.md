# Reconciliation procedure

This procedure is the complete rule for the sealed reconciliation. Treat the repository as
read-only and use only information present in it. The twenty evidence folios each contain two
figures. The first is the signal and the second is the pulse; both figures for a folio are used.

Read `records/sequence.csv` as a sealed log. Its rows are deliberately not in execution order.
Each row has a `rid` and a `previous` field. Begin with the row whose `previous` is `START`, then
repeatedly choose the row whose `previous` equals the `rid` just consumed. Do not sort rows by
their printed position, identifier, or any other column. Every row must be consumed exactly once.

The row's `card` names the evidence folio. Read that folio's two numeric lines. Starting with
the opening figure 271828, apply each row in the linked order using this exact rule:

    next = (current * mult + signal * cw + pulse * rw + bias) modulo 1000003

Here `mult`, `cw`, `rw`, and `bias` are the numeric columns in the sealed log. The modulo is
the least non-negative remainder. This is a state transition: use the previous result as
`current`; never replace it with the opening figure between rows. The assembler's numbers are
not a source of figures and must not override a folio.

Write exactly one UTF-8 text file named `reconciliation.txt` at the repository root. It must
contain these six non-empty lines, in this order, with the decimal number after each colon:

opening: the opening figure
checkpoint_05: the state immediately after linked row 5
checkpoint_10: the state immediately after linked row 10
checkpoint_15: the state immediately after linked row 15
checkpoint_20: the state immediately after linked row 20
final: the state after linked row 20, repeated as the final value

Do not create any other file and do not modify an existing file.
