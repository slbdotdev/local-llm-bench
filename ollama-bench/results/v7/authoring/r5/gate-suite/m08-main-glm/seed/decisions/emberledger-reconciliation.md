# Emberledger decision record

The reconciliation review approved a linked-state reading of the sealed records. The log is an
index, not an answer table: its predecessor links determine the walk, while the folios supply
the two figures consumed by each transition. The procedure's opening figure and modulus are
authoritative. A checkpoint is a snapshot after the stated number of consumed links.

Reviewers must preserve the evidence folios byte-for-byte. A row that cannot be reached from the
START link is a malformed sealed log. A folio may be read when its linked row calls for it, but
its figures must not be copied into a new index or summary before the walk is complete.
