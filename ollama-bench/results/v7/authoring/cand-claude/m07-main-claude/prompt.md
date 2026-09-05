You are working in a snapshot of the `kestrel-yard` repository.

The `attestation` stage is being renamed to `settlement`, and its class `AttestationEngine` is being renamed to
`SettlementLedger`. Carry out the rename across the repository.

Specifically:

- the module `src/kestrel/attestation_view.py` becomes `src/kestrel/settlement_view.py`;
- the class `AttestationEngine` becomes `SettlementLedger`;
- the module constants `DEFAULT_ATTESTATION_LIMIT`, `DEFAULT_ATTESTATION_WINDOW_S` and `ATTESTATION_STATES`
  take the new stage's name in place of the old one, and the factory function `build_attestation`
  becomes `build_settlement`;
- the stage's documentation file is renamed to match, and its history entry is **left where it
  is and left as it is** — a history entry records what was decided at the time and is not
  rewritten by a later rename.

**No occurrence of the string `attestation` or the string `AttestationEngine` may remain anywhere under
`src/`, `config/`, `tools/`, `tests/` or `docs/` when you are finished**, except inside
`history/`, which is not under any of those directories and must not be touched.

Behaviour must not change: the renamed stage keeps the same limit, the same window and the same
methods. Everything the repository says about how it is built and how it is regenerated still
has to be true afterwards.
