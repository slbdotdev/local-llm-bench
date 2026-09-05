# Multi-source batch review M-12

This is the longest human review sequence used before release freeze. It
combines all canonical source families and several source names that do not
alias. It is retained because a small isolated fixture can hide a state map
that is accidentally global.

The records arrive in this order:

1. `svc`: add err 1 with labels `A`, `a`.
2. `zeta`: add err 2 with label `B`.
3. `core`: add compile 3 with label `C`.
4. `web`: add paint 4 with label `D`.
5. `jobs`: add task 5 with label `E`.
6. `service`: remove request -1 with label `F`.
7. `platform`: hold build 10 with label `G`.
8. `ui`: void draw 99 with label `H`.
9. `worker`: remove job 2 with label `I`.
10. `zeta`: adjust err -2 with label `J`.
11. `frontend`: add draw 0 with label `K`.
12. `batch`: hold task 0 with label `L`.
13. `svc`: ignore cfg 8 with label `M`.
14. `zeta`: add warn 1 with labels `N`, `n`.
15. `platform`: add compilation -3 with label `O`.

The outer order is service, zeta, platform, frontend, worker. Aliases merge
into those positions. Service requests is created at record six after error;
the remove of -1 contributes +1. Platform build is created at record seven by
hold and then updated by compilation, for total -3 and occurrences two.
Frontend render is created by draw at record eleven because the earlier void
did not reserve it. Worker jobs is updated by a remove, and the later hold
counts. Zeta error total zero after add 2 and adjust -2, with two occurrences;
warning is appended after error.

The exact labels follow accepted-only first-seen canonical merge. Administrative
H and M are absent. The sequence is designed to require per-source positions,
per-key arithmetic, and policy sequencing in one pass.
